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


class Lease(resource.Resource):
    resources_key = 'leases'
    base_path = '/leases'

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
    )

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    id = resource.Body("uuid", alternate_id=True)
    node_type = resource.Body("resource_type")
    resource_id = resource.Body("resource_uuid")
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
    name = resource.Body("name")
    project = resource.Body("project")
    project_id = resource.Body("project_id")
    lease_resource = resource.Body("resource")
    properties = resource.Body("properties")
    purpose = resource.Body("purpose")
