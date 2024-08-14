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

from esi.lease.v1 import _proxy
from esi.lease.v1 import console_auth_token
from esi.lease.v1 import event
from esi.lease.v1 import lease
from esi.lease.v1 import node
from esi.lease.v1 import offer

from openstack.tests.unit import test_proxy_base

_MOCK_METHOD = 'esi.lease.v1._proxy.Proxy._get_with_fields'


class TestESILEAPProxy(test_proxy_base.TestProxyBase):
    def setUp(self):
        super(TestESILEAPProxy, self).setUp()
        self.proxy = _proxy.Proxy(self.session)


class TestOffer(TestESILEAPProxy):
    @mock.patch.object(offer.Offer, 'list')
    def test_offers(self, mock_list):
        result = self.proxy.offers(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, query=1)

    def test_create_offer(self):
        self.verify_create(self.proxy.create_offer, offer.Offer)

    def test_get_offer(self):
        self.verify_get(
            self.proxy.get_offer,
            offer.Offer,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_delete_offer(self):
        self.verify_delete(self.proxy.delete_offer, offer.Offer, False)

    def test_delete_offer_ignore(self):
        self.verify_delete(self.proxy.delete_offer, offer.Offer, True)


class TestLease(TestESILEAPProxy):
    @mock.patch.object(lease.Lease, 'list')
    def test_leases(self, mock_list):
        result = self.proxy.leases(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, query=1)

    def test_create_lease(self):
        self.verify_create(self.proxy.create_lease, lease.Lease)

    def test_get_lease(self):
        self.verify_get(
            self.proxy.get_lease,
            lease.Lease,
            mock_method=_MOCK_METHOD,
            expected_kwargs={'fields': None},
        )

    def test_delete_lease(self):
        self.verify_delete(self.proxy.delete_lease, lease.Lease, False)

    def test_delete_lease_ignore(self):
        self.verify_delete(self.proxy.delete_lease, lease.Lease, True)


class TestNode(TestESILEAPProxy):
    @mock.patch.object(node.Node, 'list')
    def test_nodes(self, mock_list):
        result = self.proxy.nodes()
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy)


class TestEvent(TestESILEAPProxy):
    @mock.patch.object(event.Event, 'list')
    def test_events(self, mock_list):
        result = self.proxy.events(query=1)
        self.assertIs(result, mock_list.return_value)
        mock_list.assert_called_once_with(self.proxy, query=1)


class TestConsoleAuthToken(TestESILEAPProxy):
    def test_create_console_auth_token(self):
        self.verify_create(self.proxy.create_console_auth_token,
                           console_auth_token.ConsoleAuthToken)

    def test_delete_console_auth_token(self):
        self.verify_delete(self.proxy.delete_console_auth_token,
                           console_auth_token.ConsoleAuthToken, False)
