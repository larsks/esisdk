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

from datetime import datetime, timedelta, timezone
from openstack import exceptions

from esi.tests.functional.lease import base

import os


class TestESILEAPOffer(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPOffer, self).setUp()
        self.project_id = self.conn.session.get_project_id()
        self.node_1_uuid = os.getenv("NODE_1_UUID")
        self.node_1_type = os.getenv("NODE_1_TYPE")
        self.node_2_uuid = os.getenv("NODE_2_UUID")
        self.node_2_type = os.getenv("NODE_2_TYPE")

    def test_offer_create_show_delete(self):
        offer = self.create_offer(self.node_1_uuid, self.node_1_type)

        self.assertEqual(offer.resource_uuid, self.node_1_uuid)
        self.assertEqual(offer.node_type, self.node_1_type)

        loaded = self.conn.lease.get_offer(offer.id)
        self.assertEqual(loaded.id, offer.id)
        self.assertEqual(loaded.resource_uuid, self.node_1_uuid)
        self.assertEqual(loaded.node_type, self.node_1_type)

        self.conn.lease.delete_offer(offer.id, ignore_missing=False)

        offers = self.conn.lease.offers(resource_uuid=self.node_1_uuid)
        self.assertNotIn(offer.id, [o.id for o in offers])

    def test_offer_create_detail(self):
        time_now = datetime.now(timezone.utc)
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        extra_fields = {
            "lessee_id": self.project_id,
            "start_time": start_time,
            "end_time": end_time,
        }
        offer = self.create_offer(self.node_1_uuid, self.node_1_type, **extra_fields)
        loaded = self.conn.lease.get_offer(offer.id)
        self.assertEqual(loaded.id, offer.id)
        self.assertEqual(loaded.resource_uuid, self.node_1_uuid)
        self.assertEqual(loaded.node_type, self.node_1_type)
        self.assertEqual(loaded.lessee_id, self.project_id)

    def test_offer_show_not_found(self):
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.lease.get_offer,
            "random_offer_id",
        )

    def test_offer_list(self):
        time_now = datetime.now(timezone.utc)
        start_time_1 = time_now + timedelta(minutes=5)
        end_time_1 = start_time_1 + timedelta(minutes=30)
        start_time_2 = end_time_1 + timedelta(minutes=5)
        end_time_2 = start_time_2 + timedelta(minutes=30)
        offer1 = self.create_offer(
            self.node_1_uuid,
            self.node_1_type,
            **{"start_time": start_time_1, "end_time": end_time_1},
        )
        offer2 = self.create_offer(
            self.node_1_uuid,
            self.node_1_type,
            **{"start_time": start_time_2, "end_time": end_time_2},
        )
        offer3 = self.create_offer(self.node_2_uuid, self.node_2_type)

        offers_node1 = self.conn.lease.offers(resource_uuid=self.node_1_uuid)
        offer_id_list = [o.id for o in offers_node1]
        self.assertEqual(len(offer_id_list), 2)
        for offer_id in offer1.id, offer2.id:
            self.assertIn(offer_id, offer_id_list)

        offers_node2 = self.conn.lease.offers(resource_uuid=self.node_2_uuid)
        self.assertEqual([o.id for o in offers_node2], [offer3.id])

    def test_offer_claim(self):
        offer = self.create_offer(self.node_1_uuid, self.node_1_type)
        fields = {"name": "new_lease"}
        lease = self.claim_offer(offer, **fields)
        self.assertNotEqual(lease, {})

    def test_offer_claim_multiple(self):
        offer = self.create_offer(self.node_1_uuid, self.node_1_type)
        time_now = datetime.now(timezone.utc)
        lease1_start_time = time_now + timedelta(minutes=5)
        lease1_end_time = lease1_start_time + timedelta(minutes=30)
        lease2_start_time = lease1_end_time + timedelta(minutes=5)
        lease2_end_time = lease2_start_time + timedelta(minutes=30)
        new_lease1 = {
            "name": "new_lease1",
            "start_time": lease1_start_time,
            "end_time": lease1_end_time,
        }
        new_lease2 = {
            "name": "new_lease2",
            "start_time": lease2_start_time,
            "end_time": lease2_end_time,
        }
        lease1 = self.claim_offer(offer, **new_lease1)
        self.assertNotEqual(lease1, {})

        lease2 = self.claim_offer(offer, **new_lease2)

        self.assertNotEqual(lease2, {})
        lease_list = self.conn.lease.leases(resource_uuid=self.node_1_uuid)
        uuid_list = [ls.id for ls in lease_list]
        self.assertNotEqual(lease_list, [])
        for lease_id in lease1["uuid"], lease2["uuid"]:
            self.assertIn(lease_id, uuid_list)
