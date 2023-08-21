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

from esi.lease.v1 import node
from openstack.tests.unit import base

FAKE = {'uuid': 'abc_001',
        'name': 'node_name',
        'owner': "owner_name",
        'lessee': 'lessee_name',
        'provision_state': 'available',
        'maintenance': 'false',
        'offer_uuid': 'offer_001',
        'lease_uuid': 'lease_001',
        'future_offers': None,
        'future_leases': None,
        }


class TestNode(base.TestCase):
    def test_basic(self):
        n = node.Node()
        self.assertIsNone(n.resource_key)
        self.assertEqual('nodes', n.resources_key)
        self.assertEqual('/nodes', n.base_path)
        self.assertFalse(n.allow_create)
        self.assertTrue(n.allow_fetch)
        self.assertFalse(n.allow_commit)
        self.assertFalse(n.allow_delete)
        self.assertTrue(n.allow_list)

    def test_instantiate(self):
        n = node.Node(**FAKE)
        self.assertEqual(FAKE['uuid'], n.id)
        self.assertEqual(FAKE['name'], n.name)
        self.assertEqual(FAKE['owner'], n.owner)
        self.assertEqual(FAKE['lessee'], n.lessee)
        self.assertEqual(FAKE['provision_state'], n.provision_state)
        self.assertEqual(FAKE['maintenance'], n.maintenance)
        self.assertEqual(FAKE['offer_uuid'], n.offer_id)
        self.assertEqual(FAKE['lease_uuid'], n.lease_id)
        self.assertEqual(FAKE['future_offers'], n.future_offers)
        self.assertEqual(FAKE['future_leases'], n.future_leases)
