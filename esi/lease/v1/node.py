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

from openstack import resource


class Node(resource.Resource):
    resources_key = 'nodes'
    base_path = '/nodes'

    # capabilities
    allow_create = False
    allow_fetch = True
    allow_commit = False
    allow_delete = False
    allow_list = True

    # client-side query parameter
    _query_mapping = resource.QueryParameters(
        'name',
        'owner',
        'lessee',
        'offer_uuid',
        'lease_uuid'
    )

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    id = resource.Body("uuid", alternate_id=True)
    name = resource.Body("name")
    owner = resource.Body("owner")
    lessee = resource.Body("lessee")
    provision_state = resource.Body("provision_state")
    maintenance = resource.Body("maintenance")
    offer_id = resource.Body("offer_uuid")
    lease_id = resource.Body("lease_uuid")
    future_offers = resource.Body("future_offers")
    future_leases = resource.Body("future_leases")
