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

from esi.tests.functional.lease import base
from openstack import exceptions
import os


class TestESILEAPLease(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPLease, self).setUp()
        self.project_id = self.conn.session.get_project_id()
        self.node_1_uuid = os.getenv('NODE_1_UUID')
        self.node_1_type = os.getenv('NODE_1_TYPE')
        self.node_2_uuid = os.getenv('NODE_2_UUID')
        self.node_2_type = os.getenv('NODE_2_TYPE')

    def test_lease_create_show_delete(self):
        time_now = datetime.now(timezone.utc)
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        extra_fields = {"node_type": self.node_1_type,
                        "start_time": start_time,
                        "end_time": end_time}
        lease = self.create_lease(self.node_1_uuid,
                                  self.project_id,
                                  **extra_fields)
        self.assertEqual(lease.resource_uuid, self.node_1_uuid)
        self.assertEqual(lease.project_id, self.project_id)
        self.assertEqual(lease.node_type, self.node_1_type)

        loaded = self.conn.lease.get_lease(lease.id)
        self.assertEqual(loaded.id, lease.id)
        self.assertEqual(loaded.resource_uuid, self.node_1_uuid)
        self.assertEqual(loaded.node_type, self.node_1_type)

        self.conn.lease.delete_lease(lease.id, ignore_missing=False)

        leases = self.conn.lease.leases(resource_uuid=self.node_1_uuid)
        self.assertNotIn(lease.id, [l.id for l in leases])

    def test_lease_show_not_found(self):
        self.assertRaises(
            exceptions.ResourceNotFound,
            self.conn.lease.get_lease,
            "random_lease_id",
        )

    def test_lease_list(self):
        time_now = datetime.now(timezone.utc)
        start_time_1 = time_now + timedelta(minutes=5)
        end_time_1 = start_time_1 + timedelta(minutes=30)
        start_time_2 = end_time_1 + timedelta(minutes=5)
        end_time_2 = start_time_2 + timedelta(minutes=30)
        lease1 = self.create_lease(self.node_1_uuid,
                                   self.project_id,
                                   **{"node_type": self.node_1_type,
                                      "start_time": start_time_1,
                                      "end_time": end_time_1})
        lease2 = self.create_lease(self.node_1_uuid,
                                   self.project_id,
                                   **{"node_type": self.node_1_type,
                                      "start_time": start_time_2,
                                      "end_time": end_time_2})
        lease3 = self.create_lease(self.node_2_uuid,
                                   self.project_id,
                                   node_type=self.node_2_type)
        leases_node1 = self.conn.lease.leases(resource_uuid=self.node_1_uuid)
        lease_id_list = [l.id for l in leases_node1]
        for lease_id in lease1.id, lease2.id:
            self.assertIn(lease_id, lease_id_list)

        leases_node2 = self.conn.lease.leases(resource_uuid=self.node_2_uuid)
        self.assertEqual([l.id for l in leases_node2], [lease3.id])

    def test_lease_update_valid(self):
        time_now = datetime.now(timezone.utc)
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        end_time_new = (end_time + timedelta(minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')
        extra_fields = {"node_type": self.node_1_type,
                        "start_time": start_time,
                        "end_time": end_time}
        lease = self.create_lease(self.node_1_uuid,
                                  self.project_id,
                                  **extra_fields)
        updated_lease = self.conn.lease.update_lease(lease, end_time=end_time_new)
        self.assertEqual(updated_lease.get("end_time"), end_time_new)

    def test_lease_update_invalid(self):
        time_now = datetime.now(timezone.utc).replace(microsecond=0)
        start_time = time_now + timedelta(minutes=5)
        end_time = start_time + timedelta(minutes=30)
        start_time_new = start_time + timedelta(minutes=10)
        extra_fields = {"node_type": self.node_1_type,
                        "start_time": start_time,
                        "end_time": end_time}
        lease = self.create_lease(self.node_1_uuid,
                                  self.project_id,
                                  **extra_fields)
        self.assertRaises(exceptions.HttpException,
                          self.conn.lease.update_lease,
                          lease, start_time=start_time_new)
