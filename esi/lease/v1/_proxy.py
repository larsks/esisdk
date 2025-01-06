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

from esi.lease.v1 import _common
from esi.lease.v1 import console_auth_token as _console_auth_token
from esi.lease.v1 import event as _event
from esi.lease.v1 import lease as _lease
from esi.lease.v1 import node as _node
from esi.lease.v1 import offer as _offer

from openstack import proxy


class Proxy(proxy.Proxy):
    _resource_registry = {
        "offer": _offer.Offer,
        "lease": _lease.Lease,
        "node": _node.Node,
        "event": _event.Event,
        "console_auth_token": _console_auth_token.ConsoleAuthToken,
    }
    skip_discovery = True

    def _get_with_fields(self, resource_type, value, fields=None):
        """Fetch an ESI-LEAP resource.

        :param resource_type: The type of resource to get.
        :type resource_type: :class:`~openstack.resource.Resource`
        :param value: The value to get. Can be either the ID of a
            resource or a :class:`~openstack.resource.Resource`
            subclass.
        :param fields: Limit the resource fields to fetch.

        :returns: The result of the ``fetch``
        :rtype: :class:`~openstack.resource.Resource`
        """
        res = self._get_resource(resource_type, value)
        kwargs = {}
        if fields:
            kwargs["fields"] = _common.fields_type(fields, resource_type)
        return res.fetch(
            self,
            error_message="No {resource_type} found for {value}".format(
                resource_type=resource_type.__name__, value=value
            ),
            **kwargs,
        )

    def offers(self, **query):
        """Retrieve a generator of offers.

        :param dict query: Optional query parameters to be sent to restrict
            the offers returned. Available parameters include:

            * ``status``: Only return offers with the specified status.
            * ``start_time``: Only return those with the specified ``start_time``
              or an empty set if not found.
            * ``end_time``: Only return those with the specified ``end_time``
              or an empty set if not found.
            * ``available_start_time``:  Only return those with the
                specified ``available_start_time`` or an empty set if not found.
            * ``available_end_time``:  Only return those with the
              specified ``available_start_time`` or an empty set if not found.
            * ``project_id``:only return the ones associated with this specific
              project UUID.
            * ``node_type``:only return the ones associated with this specific
              node type.
            * ``resource_uuid``:only return the ones associated with this specific
              resource uuid.
            * ``resource_class``:only return the ones associated with this specific
              resource class.

        :returns: A generator of offer instances.
        """
        return _offer.Offer.list(self, **query)

    def create_offer(self, **attrs):
        """Create a new offer from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~esi_leap.v1.offer.Offer`.

        :returns: The results of offer creation.
        :rtype: :class:`~esi_leap.v1.offer.Offer`.
        """
        return self._create(_offer.Offer, **attrs)

    def get_offer(self, offer, fields=None):
        """Get a specific offer.

        :param offer: The value can be the ID of an offer or a
            :class:`~esi_leap.v1.offer.Offer` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~esi_leap.v1.offer.Offer`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            offer matching the name or ID could be found.
        """
        return self._get_with_fields(_offer.Offer, offer, fields=fields)

    def delete_offer(self, offer, ignore_missing=False):
        """Delete an offer.

        :param offer: The value can be either the ID of an offer or
            a :class:`~esi_leap.v1.offer.Offer` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the offer could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            offer.

        :returns: The result of delete.
        :rtype: :class:`~esi_leap.v1.offer.Offer`.
        """
        return self._delete(_offer.Offer, offer, ignore_missing=ignore_missing)

    def claim_offer(self, offer, **attrs):
        """Claim an offer.

        :param offer: Either the ID of a offer or an instance
            of :class:``~esi_leap.v1.offer`.
        :param dict attrs: The attributes to update on the offer represented
            by the ``offer`` parameter.

        :returns: The claimed offer.
        :rtype: :class:`~esi.v1.offer.Offer`
        """
        res = self._get_resource(_offer.Offer, offer)
        return res.claim_offer(self, **attrs)

    def leases(self, **query):
        """Retrieve a generator of leases.

        :param dict query: Optional query parameters to be sent to restrict
            the leases returned. Available parameters include:

            * ``status``: Only return leases with the specified status.
            * ``start_time``: Only return those with the specified ``start_time``
              or an empty set if not found.
            * ``end_time``: Only return those with the specified ``end_time``
              or an empty set if not found.
            * ``project_id``:only return the ones associated with this specific
              project UUID.
            * ``owner_id``:only return the ones associated with this specific
              owner UUID.
            * ``node_type``:only return the ones associated with this specific
              node type.
            * ``resource_uuid``:only return the ones associated with this specific
              resource uuid.
            * ``resource_class``:only return the ones associated with this specific
              resource class.
            * ``purpose``:only return the ones associated with this specific
              purpose.

        :returns: A generator of lease instances.
        """
        return _lease.Lease.list(self, **query)

    def create_lease(self, **attrs):
        """Create a new lease from attributes.

        :param dict attrs: Keyword arguments that will be used to create a
            :class:`~esi_leap.v1.lease.Lease`.

        :returns: The results of lease creation.
        :rtype: :class:`~esi_leap.v1.lease.Lease`.
        """
        return self._create(_lease.Lease, **attrs)

    def update_lease(self, lease, **attrs):
        """Update a lease.

        :param lease: The value can be the ID of a lease or a
            :class:`~esi_leap.v1.lease.Lease` instance.
        :param dict attrs: The attributes to update on the lease.

        :returns: The updated lease
        :rtype: :class:`~esi_leap.v1.lease.Lease`.
        """
        res = self._get_resource(_lease.Lease, lease)
        return res.update(self, **attrs)

    def get_lease(self, lease, fields=None):
        """Get a specific lease.

        :param lease: The value can be the ID of a lease or a
            :class:`~esi_leap.v1.lease.Lease` instance.
        :param fields: Limit the resource fields to fetch.

        :returns: One :class:`~esi_leap.v1.lease.Lease`
        :raises: :class:`~openstack.exceptions.ResourceNotFound` when no
            lease matching the name or ID could be found.
        """
        return self._get_with_fields(_lease.Lease, lease, fields=fields)

    def delete_lease(self, lease, ignore_missing=False):
        """Delete a lease.

        :param lease: The value can be either the ID of a lease or
            a :class:`~esi_leap.v1.lease.Lease` instance.
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the lease could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            offer.

        :returns: The result of delete.
        :rtype: :class:`~esi_leap.v1.lease.Lease`.
        """
        return self._delete(_lease.Lease, lease, ignore_missing=ignore_missing)

    def nodes(self, **query):
        """Retrieve a generator of nodes.

        :returns: A generator of lease instances.
        """
        return _node.Node.list(self, **query)

    def events(self, **query):
        """Retrieve a generator of events.

        :param dict query: Optional query parameters to be sent to restrict
            the events returned. Available parameters include:

            * ``lessee_or_owner_id``: Only return events with the specified
              lessee_or_owner_id.
            * ``last_event_id``: Only return those with the specified last_event_id
            * ``last_event_time``: Only return those with the specified
              last_event_time
            * ``event_type``:only return the ones associated with this specific
              event_type.
            * ``node_type``:only return the ones associated with this specific
              node type.
            * ``resource_uuid``:only return the ones associated with this specific
              resource uuid.

        :returns: A generator of event instances.
        """
        return _event.Event.list(self, **query)

    def create_console_auth_token(self, **attrs):
        """Create a new console auth token from attributes.

        :param string node_uuid_or_name: node uuid or name

        :returns: The results of token creation.
        :rtype: :class:`~esi_leap.v1.console_auth_token.ConsoleAuthToken`.
        """
        return self._create(_console_auth_token.ConsoleAuthToken, **attrs)

    def delete_console_auth_token(self, node_uuid_or_name, ignore_missing=False):
        """Delete a console auth token for a node.

        :param string node_uuid_or_name: node uuid or name
        :param bool ignore_missing: When set to ``False``, an exception
            :class:`~openstack.exceptions.ResourceNotFound` will be raised
            when the node could not be found. When set to ``True``, no
            exception will be raised when attempting to delete a non-existent
            offer.

        :returns: The result of delete.
        :rtype: :class:`~esi_leap.v1.console_auth_token.ConsoleAuthToken`.
        """
        return self._delete(
            _console_auth_token.ConsoleAuthToken,
            node_uuid_or_name,
            ignore_missing=ignore_missing,
        )
