#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from collections.abc import Mapping
import string
import time

import keystoneauth1
from keystoneauth1 import discover

from esi import _log
from esi import exceptions


def urljoin(*args):
    """A custom version of urljoin that simply joins strings into a path.

    The real urljoin takes into account web semantics like when joining a url
    like /path this should be joined to http://host/path as it is an anchored
    link. We generally won't care about that in client.
    """
    return '/'.join(str(a or '').strip('/') for a in args)


def maximum_supported_microversion(adapter, client_maximum):
    """Determine the maximum microversion supported by both client and server.

    :param adapter: :class:`~keystoneauth1.adapter.Adapter` instance.
    :param client_maximum: Maximum microversion supported by the client.
        If ``None``, ``None`` is returned.

    :returns: the maximum supported microversion as string or ``None``.
    """
    if client_maximum is None:
        return None

    # NOTE(dtantsur): if we cannot determine supported microversions, fall back
    # to the default one.
    try:
        endpoint_data = adapter.get_endpoint_data()
    except keystoneauth1.exceptions.discovery.DiscoveryFailure:
        endpoint_data = None

    if endpoint_data is None:
        log = _log.setup_logging('openstack')
        log.warning(
            'Cannot determine endpoint data for service %s',
            adapter.service_type or adapter.service_name,
        )
        return None

    if not endpoint_data.max_microversion:
        return None

    client_max = discover.normalize_version_number(client_maximum)
    server_max = discover.normalize_version_number(
        endpoint_data.max_microversion
    )

    if endpoint_data.min_microversion:
        server_min = discover.normalize_version_number(
            endpoint_data.min_microversion
        )
        if client_max < server_min:
            # NOTE(dtantsur): we may want to raise in this case, but this keeps
            # the current behavior intact.
            return None

    result = min(client_max, server_max)
    return discover.version_to_string(result)


def iterate_timeout(timeout, message, wait=2):
    """Iterate and raise an exception on timeout.

    This is a generator that will continually yield and sleep for
    wait seconds, and if the timeout is reached, will raise an exception
    with <message>.

    """
    log = _log.setup_logging('openstack.iterate_timeout')

    try:
        # None as a wait winds up flowing well in the per-resource cache
        # flow. We could spread this logic around to all of the calling
        # points, but just having this treat None as "I don't have a value"
        # seems friendlier
        if wait is None:
            wait = 2
        elif wait == 0:
            # wait should be < timeout, unless timeout is None
            wait = 0.1 if timeout is None else min(0.1, timeout)
        wait = float(wait)
    except ValueError:
        raise exceptions.SDKException(
            "Wait value must be an int or float value. {wait} given"
            " instead".format(wait=wait)
        )

    start = time.time()
    count = 0
    while (timeout is None) or (time.time() < start + timeout):
        count += 1
        yield count
        log.debug('Waiting %s seconds', wait)
        time.sleep(wait)
    raise exceptions.ResourceTimeout(message)


def get_string_format_keys(fmt_string, old_style=True):
    # Gets a list of required keys from a format string
    # Required mostly for parsing base_path urls for required keys, which
    # use the old style string formatting.
    if old_style:

        class AccessSaver:
            def __init__(self):
                self.keys = []

            def __getitem__(self, key):
                self.keys.append(key)

        a = AccessSaver()
        fmt_string % a

        return a.keys
    else:
        keys = []
        for t in string.Formatter().parse(fmt_string):
            if t[1] is not None:
                keys.append(t[1])
        return keys


class Munch(dict):
    """A slightly stripped version of munch.Munch class"""

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    # only called if k not found in normal places
    def __getattr__(self, k):
        """Gets key if it exists, otherwise throws AttributeError."""
        try:
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        # Sets attribute k if it exists, otherwise sets key k. A KeyError
        # raised by set-item (only likely if you subclass Munch) will
        # propagate as an AttributeError instead.
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except Exception:
                raise AttributeError(k)
        else:
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        """Deletes attribute k if it exists, otherwise deletes key k.

        A KeyError raised by deleting the key - such as when the key is missing
        - will propagate as an AttributeError instead.
        """
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
        else:
            object.__delattr__(self, k)

    def toDict(self):
        """Recursively converts a munch back into a dictionary."""
        return unmunchify(self)

    @property
    def __dict__(self):
        return self.toDict()

    def __repr__(self):
        """Invertible* string-form of a Munch."""
        return f'{self.__class__.__name__}({dict.__repr__(self)})'

    def __dir__(self):
        return list(self.keys())

    def __getstate__(self):
        # Implement a serializable interface used for pickling.
        # See https://docs.python.org/3.6/library/pickle.html.
        return {k: v for k, v in self.items()}

    def __setstate__(self, state):
        # Implement a serializable interface used for pickling.
        # See https://docs.python.org/3.6/library/pickle.html.
        self.clear()
        self.update(state)

    @classmethod
    def fromDict(cls, d):
        """Recursively transforms a dictionary into a Munch via copy."""
        return munchify(d, cls)

    def copy(self):
        return type(self).fromDict(self)

    def update(self, *args, **kwargs):

        # Override built-in method to call custom __setitem__ method that may
        # be defined in subclasses.

        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def get(self, k, d=None):
        if k not in self:
            return d
        return self[k]

    def setdefault(self, k, d=None):
        if k not in self:
            self[k] = d
        return self[k]


def munchify(x, factory=Munch):
    """Recursively transforms a dictionary into a Munch via copy."""
    # Munchify x, using `seen` to track object cycles
    seen = dict()

    def munchify_cycles(obj):
        try:
            return seen[id(obj)]
        except KeyError:
            pass

        seen[id(obj)] = partial = pre_munchify(obj)
        return post_munchify(partial, obj)

    def pre_munchify(obj):
        if isinstance(obj, Mapping):
            return factory({})
        elif isinstance(obj, list):
            return type(obj)()
        elif isinstance(obj, tuple):
            type_factory = getattr(obj, "_make", type(obj))
            return type_factory(munchify_cycles(item) for item in obj)
        else:
            return obj

    def post_munchify(partial, obj):
        if isinstance(obj, Mapping):
            partial.update((k, munchify_cycles(obj[k])) for k in obj.keys())
        elif isinstance(obj, list):
            partial.extend(munchify_cycles(item) for item in obj)
        elif isinstance(obj, tuple):
            for item_partial, item in zip(partial, obj):
                post_munchify(item_partial, item)

        return partial

    return munchify_cycles(x)


def unmunchify(x):
    """Recursively converts a Munch into a dictionary."""

    # Munchify x, using `seen` to track object cycles
    seen = dict()

    def unmunchify_cycles(obj):
        try:
            return seen[id(obj)]
        except KeyError:
            pass

        seen[id(obj)] = partial = pre_unmunchify(obj)
        return post_unmunchify(partial, obj)

    def pre_unmunchify(obj):
        if isinstance(obj, Mapping):
            return dict()
        elif isinstance(obj, list):
            return type(obj)()
        elif isinstance(obj, tuple):
            type_factory = getattr(obj, "_make", type(obj))
            return type_factory(unmunchify_cycles(item) for item in obj)
        else:
            return obj

    def post_unmunchify(partial, obj):
        if isinstance(obj, Mapping):
            partial.update((k, unmunchify_cycles(obj[k])) for k in obj.keys())
        elif isinstance(obj, list):
            partial.extend(unmunchify_cycles(v) for v in obj)
        elif isinstance(obj, tuple):
            for value_partial, value in zip(partial, obj):
                post_unmunchify(value_partial, value)

        return partial

    return unmunchify_cycles(x)
