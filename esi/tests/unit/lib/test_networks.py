#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock
from unittest import TestCase

from esi.lib import networks
from esi.tests.unit import utils as test_utils


class TestGetPorts(TestCase):

    def setUp(self):
        super(TestGetPorts, self).setUp()
        self.neutron_port1 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "neutron_port_1",
            "fixed_ips": [{"ip_address": "1.1.1.1"}],
            "trunk_details": None
        })
        self.neutron_port2 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "neutron_port_2",
            "fixed_ips": [{"ip_address": "2.2.2.2"}],
            "trunk_details": None
        })
        self.network1 = test_utils.create_mock_object({
            "id": "network_uuid_1",
            "name": "test_network1"
        })
        self.network2 = test_utils.create_mock_object({
            "id": "network_uuid_2",
            "name": "test_network2"
        })

        self.connection = mock.Mock()

        def mock_ports(network_id=None):
            if network_id == 'network_uuid_1':
                return [self.neutron_port1]
            elif network_id == 'network_uuid_2':
                return [self.neutron_port2]
            elif network_id:
                return []
            return [self.neutron_port1, self.neutron_port2]
        self.connection.network.ports.side_effect = mock_ports

    def test_get_ports(self):
        actual = networks.get_ports(self.connection)

        expected = [
            self.neutron_port1,
            self.neutron_port2,
        ]

        self.assertEqual(actual, expected)

    def test_get_ports_network_filter(self):

        actual = networks.get_ports(self.connection, self.network1)

        expected = [
            self.neutron_port1
        ]

        self.assertEqual(actual, expected)


class TestNetworkAndPortList(TestCase):

    def setUp(self):
        super(TestNetworkAndPortList, self).setUp()
        self.network1 = test_utils.create_mock_object({
            "id": "network_uuid_1",
            "name": "test_network_1"
        })
        self.network2 = test_utils.create_mock_object({
            "id": "network_uuid_2",
            "name": "test_network_2"
        })
        self.neutron_port1 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "neutron_port_1",
            "fixed_ips": [{"ip_address": "1.1.1.1"}],
            "trunk_details": None
        })
        self.neutron_port2 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "neutron_port_2",
            "fixed_ips": [{"ip_address": "2.2.2.2"}],
            "trunk_details": None
        })
        self.floating_network = test_utils.create_mock_object({
            "id": "floating_network_id",
            "name": "floating_network"
        })
        self.floating_ip = test_utils.create_mock_object({
            "id": "floating_ip_uuid_2",
            "floating_ip_address": "8.8.8.8",
            "floating_network_id": "floating_network_id",
            "port_id": "neutron_port_uuid_2"
        })
        self.floating_ip_pfw = test_utils.create_mock_object({
            "id": "floating_ip_uuid_1",
            "floating_ip_address": "9.9.9.9",
            "floating_network_id": "floating_network_id",
            "port_id": None
        })
        self.pfw1 = test_utils.create_mock_object({
            "internal_port": 22,
            "external_port": 22,
            "internal_port_id": "neutron_port_uuid_1"
        })
        self.pfw2 = test_utils.create_mock_object({
            "internal_port": 23,
            "external_port": 23,
            "internal_port_id": "neutron_port_uuid_1"
        })

        self.connection = mock.Mock()

        def mock_find_network(name_or_id=None, ignore_missing=True):
            if name_or_id == 'test_network_1' or name_or_id == 'network_uuid_1':
                return self.network1
            elif name_or_id == 'test_network_2' or name_or_id == 'network_uuid_2':
                return self.network2
            elif name_or_id == 'floating_network' or name_or_id == 'floating_network_id':
                return self.floating_network
            return None
        self.connection.network.find_network.side_effect = mock_find_network

        def mock_ports(network_id=None):
            if network_id == 'network_uuid_1':
                return [self.neutron_port1]
            elif network_id == 'network_uuid_2':
                return [self.neutron_port2]
            elif network_id:
                return []
            return [self.neutron_port1, self.neutron_port2]
        self.connection.network.ports.side_effect = mock_ports

        def mock_port_forwardings(floating_ip=None):
            if floating_ip.id == 'floating_ip_uuid_1':
                return [self.pfw1, self.pfw2]
            return []
        self.connection.network.port_forwardings.side_effect = mock_port_forwardings

        self.connection.network.networks.\
            return_value = [self.network1, self.network2, self.floating_network]
        self.connection.network.ips.\
            return_value = [self.floating_ip, self.floating_ip_pfw]

    def test_network_and_port_list(self):
        actual = networks.network_and_port_list(self.connection)

        expected = (
            [
                self.neutron_port1,
                self.neutron_port2
            ],
            {
                'network_uuid_1': self.network1,
                'network_uuid_2': self.network2,
                'floating_network_id': self.floating_network
            },
            {
                'neutron_port_uuid_1': self.floating_ip_pfw,
                'neutron_port_uuid_2': self.floating_ip
            },
            {
                'neutron_port_uuid_1': [self.pfw1, self.pfw2]
            }
        )

        self.assertEqual(actual, expected)

    def test_network_and_port_list_network_filter(self):
        actual = networks.network_and_port_list(self.connection, self.network1)

        expected = (
            [
                self.neutron_port1,
            ],
            {
                'network_uuid_1': self.network1,
                'network_uuid_2': self.network2,
                'floating_network_id': self.floating_network
            },
            {
                'neutron_port_uuid_1': self.floating_ip_pfw,
                'neutron_port_uuid_2': self.floating_ip
            },
            {
                'neutron_port_uuid_1': [self.pfw1, self.pfw2]
            }
        )

        self.assertEqual(actual, expected)


class TestGetNetworksFromPort(TestCase):

    def setUp(self):
        super(TestGetNetworksFromPort, self).setUp()
        self.network1 = test_utils.create_mock_object({
            "id": "network_uuid_1",
            "name": "test_network_1"
        })
        self.network2 = test_utils.create_mock_object({
            "id": "network_uuid_2",
            "name": "test_network_2"
        })
        self.network3 = test_utils.create_mock_object({
            "id": "network_uuid_3",
            "name": "test_network_3"
        })
        self.neutron_port1 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "neutron_port_1",
            "fixed_ips": [{"ip_address": "1.1.1.1"}],
            "trunk_details": None
        })
        self.neutron_port2 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "neutron_port_2",
            "fixed_ips": [{"ip_address": "2.2.2.2"}],
            "trunk_details": None
        })
        self.neutron_port3 = test_utils.create_mock_object({
            "id": "neutron_port_uuid_3",
            "network_id": "network_uuid_3",
            "name": "neutron_port_3",
            "fixed_ips": [{"ip_address": "3.3.3.3"}],
            "trunk_details": {
                'sub_ports': [
                    {'port_id': 'sub_port_uuid_1'},
                    {'port_id': 'sub_port_uuid_2'},
                ]
            }
        })
        self.sub_port1 = test_utils.create_mock_object({
            "id": "sub_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "sub_port_1",
            "fixed_ips": [{"ip_address": "4.4.4.4"}],
            "trunk_details": None
        })
        self.sub_port2 = test_utils.create_mock_object({
            "id": "sub_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "sub_port_2",
            "fixed_ips": [{"ip_address": "5.5.5.5"}],
            "trunk_details": None
        })
        self.floating_network = test_utils.create_mock_object({
            "id": "floating_network_id",
            "name": "floating_network"
        })
        self.floating_ip = test_utils.create_mock_object({
            "id": "floating_ip_uuid_2",
            "floating_ip_address": "8.8.8.8",
            "floating_network_id": "floating_network_id",
            "port_id": "neutron_port_uuid_2"
        })
        self.floating_ip_pfw = test_utils.create_mock_object({
            "id": "floating_ip_uuid_1",
            "floating_ip_address": "9.9.9.9",
            "floating_network_id": "floating_network_id",
            "port_id": None
        })
        self.pfw1 = test_utils.create_mock_object({
            "internal_port": 22,
            "external_port": 22,
            "internal_port_id": "neutron_port_uuid_1"
        })
        self.pfw2 = test_utils.create_mock_object({
            "internal_port": 23,
            "external_port": 23,
            "internal_port_id": "neutron_port_uuid_1"
        })

        self.connection = mock.Mock()

        def mock_get_network(network=None):
            if network == self.network1 or network == 'network_uuid_1':
                return self.network1
            elif network == self.network2 or network == 'network_uuid_2':
                return self.network2
            elif network == self.network3 or network == 'network_uuid_3':
                return self.network3
            elif network == self.floating_network or network == 'floating_network_id':
                return self.floating_network
            return None
        self.connection.network.get_network.side_effect = mock_get_network

        def mock_get_port(port=None):
            if port == self.neutron_port1 or port == 'neutron_port_uuid_1':
                return self.neutron_port1
            elif port == self.neutron_port2 or port == 'neutron_port_uuid_2':
                return self.neutron_port2
            elif port == self.neutron_port3 or port == 'neutron_port_uuid_3':
                return self.neutron_port3
            elif port == self.sub_port1 or port == 'sub_port_uuid_1':
                return self.sub_port1
            elif port == self.sub_port2 or port == 'sub_port_uuid_2':
                return self.sub_port2
            return None
        self.connection.network.get_port.side_effect = mock_get_port

    def test_get_networks_from_port_networks_dict(self):
        networks_dict = {
            'network_uuid_1': self.network1,
            'network_uuid_2': self.network2,
            'network_uuid_3': self.network3,
            'floating_network_id': self.floating_network
        }

        actual = networks.get_networks_from_port(self.connection,
                                                 self.neutron_port1,
                                                 networks_dict=networks_dict)

        expected = (
            self.network1,
            [],
            [],
            None
        )

        self.assertEqual(actual, expected)

    def test_get_networks_from_port_ips_dict(self):
        floating_ips_dict = {
            'neutron_port_uuid_1': self.floating_ip_pfw,
            'neutron_port_uuid_2': self.floating_ip
        }

        actual = networks.get_networks_from_port(self.connection,
                                                 self.neutron_port2,
                                                 floating_ips_dict=floating_ips_dict)

        expected = (
            self.network2,
            [],
            [],
            self.floating_network
        )

        self.assertEqual(actual, expected)

    def test_get_networks_from_port_trunk(self):
        networks_dict = {
            'network_uuid_1': self.network1,
            'network_uuid_2': self.network2,
            'network_uuid_3': self.network3,
            'floating_network_id': self.floating_network
        }

        floating_ips_dict = {
            'neutron_port_uuid_1': self.floating_ip_pfw,
            'neutron_port_uuid_2': self.floating_ip
        }

        actual = networks.get_networks_from_port(self.connection,
                                                 self.neutron_port3,
                                                 networks_dict=networks_dict,
                                                 floating_ips_dict=floating_ips_dict)

        expected = (
            self.network3,
            [self.network1, self.network2],
            [self.sub_port1, self.sub_port2],
            None
        )

        self.assertEqual(actual, expected)
