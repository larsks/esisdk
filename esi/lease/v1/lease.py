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

from openstack import exceptions
from openstack import resource


class Lease(resource.Resource):
    resources_key = "leases"
    base_path = "/leases"

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    allow_patch = True
    commit_method = "PATCH"
    commit_jsonpatch = True

    # client-side query parameter
    _query_mapping = resource.QueryParameters(
        "resource_uuid",
        "resource_type",
        "status",
        "uuid",
        "project_id",
        "start_time",
        "end_time",
        "owner_id",
        "resource_class",
        "offer_uuid",
        "purpose",
        "properties",
    )

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    uuid = resource.Body("uuid", alternate_id=True)
    node_type = resource.Body("resource_type")
    resource_name = resource.Body("resource")
    resource_uuid = resource.Body("resource_uuid")
    resource_class = resource.Body("resource_class")
    offer_uuid = resource.Body("offer_uuid")
    owner = resource.Body("owner")
    owner_id = resource.Body("owner_id")
    parent_lease_uuid = resource.Body("parent_lease_uuid")
    start_time = resource.Body("start_time")
    end_time = resource.Body("end_time")
    fulfill_time = resource.Body("fulfill_time")
    expire_time = resource.Body("expire_time")
    status = resource.Body("status")
    project = resource.Body("project")
    project_id = resource.Body("project_id")
    properties = resource.Body("properties")
    resource_properties = resource.Body("resource_properties")
    purpose = resource.Body("purpose")

    _attr_aliases = {"resource_type": "node_type", "resource": "resource_name"}

    def update(self, session, **kwargs):
        """Update a lease.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :returns: The result of update.
        :rtype: Response json data.
        """
        session = self._get_session(session)

        request = self._prepare_request(requires_id=True)
        response = session.patch(
            request.url,
            json=kwargs,
            headers=request.headers,
            microversion=None,
            retriable_status_codes=None,
        )

        msg = "Failed to update lease {lease} ".format(lease=self.id)
        exceptions.raise_from_response(response, error_message=msg)
        return response.json()
