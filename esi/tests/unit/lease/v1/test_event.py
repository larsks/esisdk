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

import datetime

from esi.lease.v1 import event
from openstack.tests.unit import base

event_time = datetime.datetime(2023, 7, 16, 19, 20, 30)

FAKE = {
    "id": "abc_001",
    "event_type": "notification",
    "last_event_time": event_time,
    "last_event_id": "001",
    "event_time": event_time,
    "event_id": "001",
    "lessee_or_owner_id": "lease_or_id",
    "object_type": "offer",
    "object_uuid": "offer_001",
    "resource_type": "baremetal",
    "resource_uuid": "bm_node_001",
    "lessee_id": "lessee_id",
    "owner_id": "owner_id",
}


class TestEvent(base.TestCase):
    def test_basic(self):
        e = event.Event()
        self.assertIsNone(e.resource_key)
        self.assertEqual("events", e.resources_key)
        self.assertEqual("/events", e.base_path)
        self.assertTrue(e.allow_create)
        self.assertTrue(e.allow_fetch)
        self.assertTrue(e.allow_commit)
        self.assertTrue(e.allow_delete)
        self.assertTrue(e.allow_list)
        self.assertEqual("PATCH", e.commit_method)

    def test_instantiate(self):
        e = event.Event(**FAKE)
        self.assertEqual(FAKE["id"], e.id)
        self.assertEqual(FAKE["event_type"], e.event_type)
        self.assertEqual(FAKE["last_event_time"], e.last_event_time)
        self.assertEqual(FAKE["last_event_id"], e.last_event_id)
        self.assertEqual(FAKE["lessee_or_owner_id"], e.lessee_or_owner_id)
        self.assertEqual(FAKE["event_id"], e.last_event_id)
        self.assertEqual(FAKE["event_time"], e.event_time)
        self.assertEqual(FAKE["lessee_or_owner_id"], e.lessee_or_owner_id)
        self.assertEqual(FAKE["object_type"], e.object_type)
        self.assertEqual(FAKE["object_uuid"], e.object_uuid)
        self.assertEqual(FAKE["resource_type"], e.node_type)
        self.assertEqual(FAKE["resource_uuid"], e.resource_uuid)
        self.assertEqual(FAKE["lessee_id"], e.lessee_id)
        self.assertEqual(FAKE["owner_id"], e.owner_id)
