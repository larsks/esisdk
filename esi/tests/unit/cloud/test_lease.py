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

from unittest import mock

from esi import connection
from esi.tests import fakes

from keystoneauth1.identity import base as ks_base

from openstack.tests.unit import base


# mock keystoneauth1.identity.base.get_endpoint_data because there is
# no 'lease' service in openstack.os-service-types
@mock.patch.object(
    ks_base.BaseIdentityPlugin,
    "get_endpoint_data",
    return_value=fakes.get_lease_endpoint(),
)
class TestLease(base.TestCase):
    def setUp(self):
        super(TestLease, self).setUp()
        self.fake_offer = fakes.make_fake_offer(
            "fake_offer_id", "fake_node_id", "fake_type"
        )
        self.fake_lease = fakes.make_fake_lease(
            "fake_lease_id", "fake_node_id", "fake_type", "fake_offer_id"
        )
        self.fake_node = fakes.make_fake_node(
            "fake_node_id", "fake_offer_id", "fake_lease_id"
        )
        self.fake_node_1 = fakes.make_fake_node(
            "fake_node_id_1", "fake_offer_id_1", "fake_lease_id_1"
        )
        self.fake_event = fakes.make_fake_event(
            "fake_event_id", "fake_type", "fake_time"
        )
        self.fake_event_1 = fakes.make_fake_event(
            "fake_event_id_1", "fake_type", "fake_time_1"
        )
        self.cloud_config = self.config.get_one(cloud="_test_cloud_", validate=True)
        self.cloud = connection.ESIConnection(
            config=self.cloud_config, strict=self.strict_cloud
        )
        self.uri_offer = "https://lease.example.com/v1/offers"
        self.uri_lease = "https://lease.example.com/v1/leases"
        self.uri_node = "https://lease.example.com/v1/nodes"
        self.uri_event = "https://lease.example.com/v1/events"

    def test_list_offers(self, mock_ged):
        fake_offer_1 = fakes.make_fake_offer(
            "fake_offer_id_1", "fake_node_id_1", "fake_type"
        )
        # Mock a list of URIs and responses via requests mock
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.uri_offer,
                    json={"offers": [self.fake_offer, fake_offer_1]},
                ),
            ]
        )
        offers = self.cloud.list_offers()
        self.assertEqual(2, len(offers))
        self.assertSubdict(self.fake_offer, offers[0])
        self.assertSubdict(fake_offer_1, offers[1])
        self.assert_calls()

    def test_create_offer(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="POST",
                    uri=self.uri_offer,
                    json=self.fake_offer,
                ),
            ]
        )
        offer = self.cloud.create_offer(
            resource_uuid="fake_node_id", node_type="fake_type"
        )
        self.assertEqual(offer.resource_uuid, self.fake_offer.resource_uuid)
        self.assertEqual(offer.node_type, self.fake_offer.node_type)

        self.assert_calls()

    def test_delete_offer(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="DELETE",
                    uri=self.uri_offer + "/fake_offer_id",
                    json={},
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_offer("fake_offer_id"))
        self.assert_calls()

    def test_claim_offer(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="POST",
                    uri=self.uri_offer + "/fake_offer_id/claim",
                    json=self.fake_lease,
                ),
            ]
        )
        rep_json = self.cloud.claim_offer(self.fake_offer)
        self.assertEqual(rep_json["resource_uuid"], self.fake_lease.resource_uuid)
        self.assertEqual(rep_json["node_type"], self.fake_lease.node_type)
        self.assertEqual(rep_json["offer_uuid"], self.fake_offer.id)
        self.assert_calls()

    def test_list_leases(self, mock_ged):
        fake_lease_1 = fakes.make_fake_lease(
            "fake_lease_id_1", "fake_lease_id_1", "fake_type", "fake_offer_uuid_1"
        )
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.uri_lease,
                    json={"leases": [self.fake_lease, fake_lease_1]},
                ),
            ]
        )
        leases = self.cloud.list_leases()
        self.assertEqual(2, len(leases))
        self.assertSubdict(self.fake_lease, leases[0])
        self.assertSubdict(fake_lease_1, leases[1])
        self.assert_calls()

    def test_create_lease(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="POST",
                    uri=self.uri_lease,
                    json=self.fake_lease,
                ),
            ]
        )
        lease = self.cloud.create_lease(
            resource_uuid="fake_node_id",
            node_type="fake_type",
            project_id="fake_project",
        )
        self.assertEqual(lease.resource_uuid, self.fake_lease.resource_uuid)
        self.assertEqual(lease.node_type, self.fake_lease.node_type)

        self.assert_calls()

    def test_delete_lease(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="DELETE",
                    uri=self.uri_lease + "/fake_lease_id",
                    json={},
                ),
            ]
        )
        self.assertTrue(self.cloud.delete_lease("fake_lease_id"))
        self.assert_calls()

    def test_list_nodes(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.uri_node,
                    json={"nodes": [self.fake_node, self.fake_node_1]},
                ),
            ]
        )
        nodes = self.cloud.list_nodes()
        self.assertEqual(2, len(nodes))
        self.assertSubdict(self.fake_node, nodes[0])
        self.assertSubdict(self.fake_node_1, nodes[1])
        self.assert_calls()

    def test_list_events(self, mock_ged):
        self.register_uris(
            [
                dict(
                    method="GET",
                    uri=self.uri_event,
                    json={"events": [self.fake_event, self.fake_event_1]},
                ),
            ]
        )
        events = self.cloud.list_events()
        self.assertEqual(2, len(events))
        self.assertSubdict(self.fake_event, events[0])
        self.assertSubdict(self.fake_event_1, events[1])
        self.assert_calls()
