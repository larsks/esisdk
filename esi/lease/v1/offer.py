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
from openstack import utils


class Offer(resource.Resource):
    resources_key = 'offers'
    base_path = '/offers'

    # capabilities
    allow_create = True
    allow_fetch = True
    allow_commit = True
    allow_delete = True
    allow_list = True
    commit_method = 'PATCH'
    commit_jsonpatch = True

    # client-side query parameter
    _query_mapping = resource.QueryParameters(
        'resource_uuid',
        'resource_type',
        'status',
        'uuid',
        'lessee',
    )

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    id = resource.Body("uuid", alternate_id=True)
    node_type = resource.Body("resource_type")
    resource_id = resource.Body("resource_uuid")
    resource_class = resource.Body("resource_class")
    lessee = resource.Body("lessee")
    lessee_id = resource.Body("lessee_id")
    parent_lease_uuid = resource.Body("parent_lease_uuid")
    start_time = resource.Body("start_time")
    end_time = resource.Body("end_time")
    status = resource.Body("status")
    availabilities = resource.Body("availabilities")
    name = resource.Body("name")
    project = resource.Body("project")
    project_id = resource.Body("project_id")
    offer_resource = resource.Body("resource")
    properties = resource.Body("properties")

    def claim_offer(self, session, **kwargs):
        """Claim an offer.

        :param session: The session to use for making this request.
        :type session: :class:`~keystoneauth1.adapter.Adapter`

        :returns: The result of claim.
        :rtype: Response json data.
        """
        session = self._get_session(session)

        request = self._prepare_request(requires_id=True)
        request.url = utils.urljoin(request.url, 'claim')
        response = session.post(
            request.url,
            json=kwargs,
            headers=request.headers,
            microversion=None,
            retriable_status_codes=None,
        )

        msg = (
            "Failed to claim offer {offer} ".format(offer=self.id)
        )
        exceptions.raise_from_response(response, error_message=msg)
        return response.json()
