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

from esi.tests.functional.lease import base
import os


class TestESILEAPEvent(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPEvent, self).setUp()
        self.project_id = self.conn.session.get_project_id()
        self.node_1_uuid = os.getenv("NODE_1_UUID")
        self.node_1_type = os.getenv("NODE_1_TYPE")
        self.last_event_id = os.getenv("LAST_EVENT_ID")

    def test_event_list(self):
        """Tests functionality "esi event list" using node_uuid or node name.
        checks node_uuid or node_name is present in event list or not.
        Test steps:
        1) Create a lease for a node
        2) Run event list with the last event id
        3) Checks that the output of "event list" contains
           the node uuid it's tested with."""

        self.create_lease(self.node_1_uuid, self.project_id, node_type=self.node_1_type)
        events = self.conn.lease.events(last_event_id=self.last_event_id)
        self.assertNotEqual(events, [])
        self.assertIn(self.node_1_uuid, [x["resource_uuid"] for x in events])
