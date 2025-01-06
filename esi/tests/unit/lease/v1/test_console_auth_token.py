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

from esi.lease.v1 import console_auth_token
from openstack.tests.unit import base


FAKE = {
    "node_uuid": "node_001",
    "token": "fake_token",
    "access_url": "ws://0.0.0.0:7777?token=fake_token",
}


class TestConsoleAuthToken(base.TestCase):
    def test_basic(self):
        c = console_auth_token.ConsoleAuthToken()
        self.assertIsNone(c.resource_key)
        self.assertEqual("console_auth_tokens", c.resources_key)
        self.assertEqual("/console_auth_tokens", c.base_path)
        self.assertTrue(c.allow_create)
        self.assertFalse(c.allow_fetch)
        self.assertTrue(c.allow_commit)
        self.assertTrue(c.allow_delete)
        self.assertFalse(c.allow_list)
        self.assertEqual("PATCH", c.commit_method)

    def test_instantiate(self):
        c = console_auth_token.ConsoleAuthToken(**FAKE)
        self.assertEqual(FAKE["node_uuid"], c.node_uuid)
        self.assertEqual(FAKE["token"], c.token)
        self.assertEqual(FAKE["access_url"], c.access_url)
