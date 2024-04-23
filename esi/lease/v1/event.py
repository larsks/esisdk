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


class Event(resource.Resource):
    resources_key = 'events'
    base_path = '/events'

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
        'last_event_id',
        'event_type',
        'last_event_time',
        'resource_type',
        'resource_uuid',
        'lessee_or_owner_id'
    )

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    id = resource.Body("id", alternate_id=True)
    event_type = resource.Body("event_type")
    last_event_id = resource.Body("last_event_id")
    last_event_time = resource.Body("last_event_time")
    event_id = resource.Body("event_id")
    event_time = resource.Body("event_time")
    object_type = resource.Body("object_type")
    object_uuid = resource.Body("object_uuid")
    node_type = resource.Body("resource_type")
    resource_uuid = resource.Body("resource_uuid")
    lessee_or_owner_id = resource.Body("lessee_or_owner_id")
    lessee_id = resource.Body("lessee_id")
    owner_id = resource.Body("owner_id")

    _attr_aliases = {'resource_type': 'node_type'}
