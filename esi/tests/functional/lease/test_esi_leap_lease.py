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

from esi.tests.functional.lease import base
from openstack import exceptions


class TestESILEAPLease(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPLease, self).setUp()
        self.project_id = self.conn.session.get_project_id()

    def test_lease_create_show_delete(self):
        time_now = datetime.now()
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        extra_fields = {"node_type": "dummy_node",
                        "start_time": start_time,
                        "end_time": end_time}
        lease = self.create_lease('1719',
                                  self.project_id,
                                  **extra_fields)
        self.assertEqual(lease.resource_id, '1719')
        self.assertEqual(lease.project_id, self.project_id)
        self.assertEqual(lease.node_type, 'dummy_node')

        loaded = self.conn.lease.get_lease(lease.id)
        self.assertEqual(loaded.id, lease.id)
        self.assertEqual(loaded.resource_id, '1719')
        self.assertEqual(loaded.node_type, 'dummy_node')

        self.conn.lease.delete_lease(lease.id, ignore_missing=False)

        leases = self.conn.lease.leases(resource_id='1719')
        self.assertNotIn(lease.id, [l.id for l in leases])

    def test_lease_show_not_found(self):
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.lease.get_lease,
            "random_lease_id",
        )

    def test_lease_list(self):
        time_now = datetime.now()
        start_time_1 = time_now + timedelta(minutes=5)
        end_time_1 = start_time_1 + timedelta(minutes=30)
        start_time_2 = end_time_1 + timedelta(minutes=5)
        end_time_2 = start_time_2 + timedelta(minutes=30)
        lease1 = self.create_lease('1719',
                                   self.project_id,
                                   **{"node_type": "dummy_node",
                                      "start_time": start_time_1,
                                      "end_time": end_time_1})
        lease2 = self.create_lease('1719',
                                   self.project_id,
                                   **{"node_type": "dummy_node",
                                      "start_time": start_time_2,
                                      "end_time": end_time_2})
        lease3 = self.create_lease('1720',
                                   self.project_id,
                                   node_type='dummy_node')
        leases_1719 = self.conn.lease.leases(resource_id='1719')
        lease_id_list = [l.id for l in leases_1719]
        for lease_id in lease1.id, lease2.id:
            self.assertIn(lease_id, lease_id_list)

        leases_1720 = self.conn.lease.leases(resource_id='1720')
        self.assertEqual([l.id for l in leases_1720], [lease3.id])
