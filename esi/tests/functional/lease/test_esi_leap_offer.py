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

from datetime import datetime, timedelta
from openstack import exceptions

from esi.tests.functional.lease import base


class TestESILEAPOffer(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPOffer, self).setUp()
        self.project_id = self.conn.session.get_project_id()

    def test_offer_create_show_delete(self):
        offer = self.create_offer('1719', 'dummy_node')

        self.assertEqual(offer.resource_id, '1719')
        self.assertEqual(offer.node_type, 'dummy_node')

        loaded = self.conn.lease.get_offer(offer.id)
        self.assertEqual(loaded.id, offer.id)
        self.assertEqual(loaded.resource_id, '1719')
        self.assertEqual(loaded.node_type, 'dummy_node')

        self.conn.lease.delete_offer(offer.id, ignore_missing=False)

        offers = self.conn.lease.offers(resource_id='1719')
        self.assertNotIn(offer.id, [o.id for o in offers])

    def test_offer_create_detail(self):
        time_now = datetime.now()
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        extra_fields = {"lessee_id": self.project_id,
                        "start_time": start_time,
                        "end_time": end_time}
        offer = self.create_offer('1719', 'dummy_node', **extra_fields)
        loaded = self.conn.lease.get_offer(offer.id)
        self.assertEqual(loaded.id, offer.id)
        self.assertEqual(loaded.resource_id, '1719')
        self.assertEqual(loaded.node_type, 'dummy_node')
        self.assertEqual(loaded.lessee_id, self.project_id)

    def test_offer_show_not_found(self):
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.lease.get_offer,
            "random_offer_id",
        )

    def test_offer_list(self):
        time_now = datetime.now()
        start_time_1 = time_now + timedelta(minutes=5)
        end_time_1 = start_time_1 + timedelta(minutes=30)
        start_time_2 = end_time_1 + timedelta(minutes=5)
        end_time_2 = start_time_2 + timedelta(minutes=30)
        offer1 = self.create_offer('1719', 'dummy_node',
                                   **{"start_time": start_time_1,
                                      "end_time": end_time_1})
        offer2 = self.create_offer('1719', 'dummy_node',
                                   **{"start_time": start_time_2,
                                      "end_time": end_time_2})
        offer3 = self.create_offer('1720', 'dummy_node')

        offers_1719 = self.conn.lease.offers(resource_id='1719')
        offer_id_list = [o.id for o in offers_1719]
        self.assertEqual(len(offer_id_list), 2)
        for offer_id in offer1.id, offer2.id:
            self.assertIn(offer_id, offer_id_list)

        offers_1720 = self.conn.lease.offers(resource_id='1720')
        self.assertEqual([o.id for o in offers_1720], [offer3.id])

    def test_offer_claim(self):
        offer = self.create_offer('1719', 'dummy_node')
        fields = {"name": "new_lease"}
        lease = self.conn.lease.claim_offer(offer, **fields)
        self.assertNotEqual(lease, {})

    def test_offer_claim_multiple(self):
        offer = self.create_offer('1719', 'dummy_node')
        time_now = datetime.now()
        lease1_start_time = time_now + timedelta(minutes=5)
        lease1_end_time = lease1_start_time + timedelta(minutes=30)
        lease2_start_time = lease1_end_time + timedelta(minutes=5)
        lease2_end_time = lease2_start_time + timedelta(minutes=30)
        new_lease1 = {"name": "new_lease1",
                      "start_time": lease1_start_time,
                      "end_time": lease1_end_time}
        new_lease2 = {"name": "new_lease2",
                      "start_time": lease2_start_time,
                      "end_time": lease2_end_time}
        lease1 = self.conn.lease.claim_offer(offer, **new_lease1)
        self.assertNotEqual(lease1, {})

        lease2 = self.conn.lease.claim_offer(offer, **new_lease2)

        self.assertNotEqual(lease2, {})
        lease_list = self.conn.lease.leases(resource_id='1719')
        uuid_list = [l.id for l in lease_list]
        self.assertNotEqual(lease_list, [])
        for lease_id in lease1["uuid"], lease2["uuid"]:
            self.assertIn(lease_id, uuid_list)
