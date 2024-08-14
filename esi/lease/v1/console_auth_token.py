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


class ConsoleAuthToken(resource.Resource):
    resources_key = 'console_auth_tokens'
    base_path = '/console_auth_tokens'

    # capabilities
    allow_create = True
    allow_fetch = False
    allow_commit = True
    allow_delete = True
    allow_list = False
    commit_method = 'PATCH'
    commit_jsonpatch = True

    #: The transaction date and time.
    timestamp = resource.Header("x-timestamp")
    #: The value of the resource. Also available in headers.
    node_uuid = resource.Body("node_uuid", alternate_id=True)
    node_uuid_or_name = resource.Body("node_uuid_or_name")
    token = resource.Body("token")
    access_url = resource.Body("access_url")
