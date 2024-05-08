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

from esi.lease.v1 import _proxy
from openstack import service_description

import warnings

from openstack import exceptions
from openstack import warnings as os_warnings


class LeaseService(service_description.ServiceDescription):
    """The esi-leap lease service."""

    supported_versions = {
        '1': _proxy.Proxy,
    }

    def _make_proxy(self, instance):
        """Override _make_proxy() for esi lease service.

        :param instance:
          The `esi.connection.Connection` we're working with.
        """
        config = instance.config

        # Check to see if we've got config that matches what we
        # understand in the SDK.
        version_string = config.get_api_version('lease')
        endpoint_override = config.get_endpoint('lease')

        # If the user doesn't give a version in config, but we only support
        # one version, then just use that version.
        if not version_string:
            version_string = list(self.supported_versions)[0]

        proxy_obj = None
        if endpoint_override and version_string:
            # Both endpoint override and version_string are set, we don't
            # need to do discovery - just trust the user.
            proxy_class = self.supported_versions.get(version_string[0])
            if proxy_class:
                proxy_obj = config.get_session_client(
                    'lease',
                    constructor=proxy_class,
                )
            else:
                warnings.warn(
                    f"The configured version, {version_string} for service "
                    f"lease is not known or supported by "
                    f"esisdk. The resulting Proxy object will only "
                    f"have direct passthrough REST capabilities.",
                    category=os_warnings.UnsupportedServiceVersion,
                )
        elif endpoint_override:
            temp_adapter = config.get_session_client('lease')
            api_version = temp_adapter.get_endpoint_data().api_version
            proxy_class = self.supported_versions.get(str(api_version[0]))
            if proxy_class:
                proxy_obj = config.get_session_client(
                    'lease',
                    constructor=proxy_class,
                )
            else:
                warnings.warn(
                    f"Service lease has an endpoint override "
                    f"set but the version discovered at that endpoint, "
                    f"{api_version}, is not supported by esisdk. "
                    f"The resulting Proxy object will only have direct "
                    f"passthrough REST capabilities.",
                    category=os_warnings.UnsupportedServiceVersion,
                )

        if proxy_obj:
            data = proxy_obj.get_endpoint_data()
            if not data and instance._strict_proxies:
                raise exceptions.ServiceDiscoveryException(
                    "Failed to create a working proxy for service "
                    "lease: No endpoint data found."
                )

            # If we've gotten here with a proxy object it means we have
            # an endpoint_override in place. If the catalog_url and
            # service_url don't match, which can happen if there is a
            # None plugin and auth.endpoint like with standalone ironic,
            # we need to be explicit that this service has an endpoint_override
            # so that subsequent discovery calls don't get made incorrectly.
            if data.catalog_url != data.service_url:
                ep_key = 'lease_endpoint_override'
                config.config[ep_key] = data.service_url
                proxy_obj = config.get_session_client(
                    'lease',
                    constructor=proxy_class,
                )
            return proxy_obj

        # Make an adapter to let discovery take over
        version_kwargs = {}
        if version_string:
            version_kwargs['version'] = version_string
            if getattr(
                self.supported_versions[str(version_string)],
                'skip_discovery',
                False,
            ):
                # set the endpoint_override to the current
                # catalog endpoint value + version number,
                # otherwise next request will try to perform discovery.
                temp_adapter = config.get_session_client('lease')
                ep_override = temp_adapter.get_endpoint(skip_discovery=True)
                ep_key = '{service_type}_endpoint_override'.format(
                    service_type=self.service_type.replace('-', '_')
                )
                config.config[ep_key] = '{}/v{}'.format(
                    ep_override, version_string)
                return config.get_session_client(
                    'lease',
                    allow_version_hack=True,
                    constructor=self.supported_versions[
                        str(version_string)
                    ],
                    **version_kwargs,
                )
        else:
            supported_versions = sorted(
                [int(f) for f in self.supported_versions]
            )
            version_kwargs['min_version'] = str(supported_versions[0])
            version_kwargs['max_version'] = '{version}.latest'.format(
                version=str(supported_versions[-1])
            )

        temp_adapter = config.get_session_client(
            'lease', allow_version_hack=True, **version_kwargs
        )
        found_version = temp_adapter.get_api_major_version()
        if found_version is None:
            region_name = instance.config.get_region_name(self.service_type)
            if version_kwargs:
                raise exceptions.NotSupported(
                    "The lease service for {cloud}:{region_name}"
                    " exists but does not have any supported versions.".format(
                        cloud=instance.name,
                        region_name=region_name,
                    )
                )
            else:
                raise exceptions.NotSupported(
                    "The lease service for {cloud}:{region_name}"
                    " exists but no version was discoverable.".format(
                        cloud=instance.name,
                        region_name=region_name,
                    )
                )
        proxy_class = self.supported_versions.get(str(found_version[0]))
        if proxy_class:
            return config.get_session_client(
                'lease',
                allow_version_hack=True,
                constructor=proxy_class,
                **version_kwargs,
            )

        # No proxy_class
        # Maybe esisdk is being used for the passthrough
        # REST API proxy layer for an unknown service in the
        # service catalog that also doesn't have any useful
        # version discovery?
        warnings.warn(
            "Service lease has no discoverable version. "
            "The resulting Proxy object will only have direct "
            "passthrough REST capabilities.",
            category=os_warnings.UnsupportedServiceVersion,
        )
        return temp_adapter
