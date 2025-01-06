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

from esi.lease.v1 import lease
from keystoneauth1 import adapter

from openstack import exceptions
from openstack.tests.unit import base
from unittest import mock

start = datetime.datetime(2016, 7, 16, 19, 20, 30)
FAKE = {
    "uuid": "lease_uuid",
    "resource_type": "dummy_node",
    "resource_uuid": "1718",
    "resource_class": "test",
    "offer_uuid": "offer_001",
    "owner": "owner_name",
    "owner_uuid": "owner_001",
    "parent_lease_uuid": "parent_lease_uuid",
    "start_time": start,
    "end_time": start + datetime.timedelta(days=100),
    "fulfill_time": start,
    "expire_time": start + datetime.timedelta(days=101),
    "status": "available",
    "name": "offer_name",
    "project": "project_name",
    "project_id": "project_id",
    "properties": None,
    "purpose": "test",
    "resource_properties": None,
    "resource_name": "node-1819",
}


class TestLease(base.TestCase):
    def test_basic(self):
        ls = lease.Lease()
        self.assertIsNone(ls.resource_key)
        self.assertEqual("leases", ls.resources_key)
        self.assertEqual("/leases", ls.base_path)
        self.assertTrue(ls.allow_create)
        self.assertTrue(ls.allow_fetch)
        self.assertTrue(ls.allow_commit)
        self.assertTrue(ls.allow_delete)
        self.assertTrue(ls.allow_patch)
        self.assertTrue(ls.allow_list)
        self.assertEqual("PATCH", ls.commit_method)

    def test_instantiate(self):
        ls = lease.Lease(**FAKE)
        self.assertEqual(FAKE["uuid"], ls.uuid)
        self.assertEqual(FAKE["resource_uuid"], ls.resource_uuid)
        self.assertEqual(FAKE["resource_type"], ls.node_type)
        self.assertEqual(FAKE["resource_class"], ls.resource_class)
        self.assertEqual(FAKE["parent_lease_uuid"], ls.parent_lease_uuid)
        self.assertEqual(FAKE["start_time"], ls.start_time)
        self.assertEqual(FAKE["end_time"], ls.end_time)
        self.assertEqual(FAKE["fulfill_time"], ls.fulfill_time)
        self.assertEqual(FAKE["expire_time"], ls.expire_time)
        self.assertEqual(FAKE["status"], ls.status)
        self.assertEqual(FAKE["name"], ls.name)
        self.assertEqual(FAKE["project"], ls.project)
        self.assertEqual(FAKE["project_id"], ls.project_id)
        self.assertEqual(FAKE["properties"], ls.properties)
        self.assertEqual(FAKE["purpose"], ls.purpose)
        self.assertEqual(FAKE["resource_properties"], ls.resource_properties)
        self.assertEqual(FAKE["resource_name"], ls.resource_name)


@mock.patch.object(exceptions, "raise_from_response", mock.Mock())
class TestLeaseUpdate(object):
    def setUp(self):
        super(TestLeaseUpdate, self).setUp()
        self.lease = lease.Lease(**FAKE)
        self.session = lease.Mock(spec=adapter.Adapter, default_microversion=None)
        self.session.log = mock.Mock()

    def test_update_lease(self):
        self.lease.update(self.session)
        self.session.get.assert_called_once_with(
            "lease/%s" % self.lease.id,
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=None,
        )
