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

from keystoneauth1 import adapter

from esi.lease.v1 import offer
from openstack import exceptions
from openstack.tests.unit import base
from unittest import mock


start = datetime.datetime(2016, 7, 16, 19, 20, 30)
FAKE = {'uuid': 'offer_uuid',
        'resource_type': 'dummy_node',
        'resource_uuid': '1718',
        'resource_class': "test",
        'lessee': 'lessee_001',
        'lessee_id': "lessee_id",
        'parent_lease_uuid': 'parent_lease_uuid',
        'start_time': start,
        'end_time': start + datetime.timedelta(days=100),
        'status': 'available',
        'available_start_time': start,
        'available_end_time': start + datetime.timedelta(days=101),
        'availabilities': None,
        'name': 'offer_name',
        'project': 'project_name',
        'project_id': 'project_id',
        'resource_name': 'resource',
        'properties': None,
        'resource_properties': None
        }


class TestOffer(base.TestCase):
    def test_basic(self):
        o = offer.Offer()
        self.assertIsNone(o.resource_key)
        self.assertEqual('offers', o.resources_key)
        self.assertEqual('/offers', o.base_path)
        self.assertTrue(o.allow_create)
        self.assertTrue(o.allow_fetch)
        self.assertTrue(o.allow_commit)
        self.assertTrue(o.allow_delete)
        self.assertTrue(o.allow_list)
        self.assertEqual('PATCH', o.commit_method)

    def test_instantiate(self):
        o = offer.Offer(**FAKE)
        self.assertEqual(FAKE['uuid'], o.uuid)
        self.assertEqual(FAKE['resource_uuid'], o.resource_uuid)
        self.assertEqual(FAKE['resource_type'], o.node_type)
        self.assertEqual(FAKE['resource_class'], o.resource_class)
        self.assertEqual(FAKE['lessee'], o.lessee)
        self.assertEqual(FAKE['lessee_id'], o.lessee_id)
        self.assertEqual(FAKE['parent_lease_uuid'], o.parent_lease_uuid)
        self.assertEqual(FAKE['start_time'], o.start_time)
        self.assertEqual(FAKE['end_time'], o.end_time)
        self.assertEqual(FAKE['status'], o.status)
        self.assertEqual(FAKE['available_start_time'],
                         o.available_start_time)
        self.assertEqual(FAKE['available_end_time'],
                         o.available_end_time)
        self.assertEqual(FAKE['availabilities'], o.availabilities)
        self.assertEqual(FAKE['name'], o.name)
        self.assertEqual(FAKE['project'], o.project)
        self.assertEqual(FAKE['project_id'], o.project_id)
        self.assertEqual(FAKE['resource_name'], o.resource_name)
        self.assertEqual(FAKE['properties'], o.properties)
        self.assertEqual(FAKE['resource_properties'],
                         o.resource_properties)


@mock.patch.object(exceptions, 'raise_from_response', mock.Mock())
class TestOfferClaim(object):
    def setUp(self):
        super(TestOfferClaim, self).setUp()
        self.offer = offer.Offer(**FAKE)
        self.session = offer.Mock(
            spec=adapter.Adapter, default_microversion=None
        )
        self.session.log = mock.Mock()

    def test_claim_offer(self):
        self.offer.claim_offer(self.session)
        self.session.get.assert_called_once_with(
            'offer/%s/claim' % self.offer.id,
            headers=mock.ANY,
            microversion=None,
            retriable_status_codes=None,
        )
