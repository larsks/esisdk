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

import mock
from unittest import TestCase

from esi.lib import nodes

from esi.tests.unit import utils


class TestNodeAndPortList(TestCase):

    def setUp(self):
        super(TestNodeAndPortList, self).setUp()
        self.maxDiff = None

        self.port1 = utils.create_mock_object({
            "uuid": "port_uuid_1",
            "node_id": "11111111-2222-3333-4444-aaaaaaaaaaaa",
            "address": "aa:aa:aa:aa:aa:aa",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_1'}
        })
        self.port2 = utils.create_mock_object({
            "uuid": "port_uuid_2",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "bb:bb:bb:bb:bb:bb",
            "internal_info": {}
        })
        self.port3 = utils.create_mock_object({
            "uuid": "port_uuid_3",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "cc:cc:cc:cc:cc:cc",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_2'}
        })
        self.port4 = utils.create_mock_object({
            "uuid": "port_uuid_4",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "dd:dd:dd:dd:dd:dd",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_4'}
        })
        self.node1 = utils.create_mock_object({
            "id": "11111111-2222-3333-4444-aaaaaaaaaaaa",
            "name": "node1"
        })
        self.node2 = utils.create_mock_object({
            "id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "name": "node2"
        })

        self.connection = mock.Mock()

        def mock_find_node(name_or_id=None, ignore_missing=True):
            if name_or_id == "11111111-2222-3333-4444-aaaaaaaaaaaa" or name_or_id == "node1":
                return self.node1
            elif name_or_id == "11111111-2222-3333-4444-bbbbbbbbbbbb" or name_or_id == "node2":
                return self.node2
        self.connection.baremetal.find_node.side_effect = mock_find_node

        def mock_baremetal_ports(details=False, node_id=None):
            if node_id == '11111111-2222-3333-4444-aaaaaaaaaaaa':
                return [self.port1]
            if node_id == '11111111-2222-3333-4444-bbbbbbbbbbbb':
                return [self.port2, self.port3, self.port4]
            return [self.port1, self.port2, self.port3, self.port4]
        self.connection.baremetal.ports.side_effect = mock_baremetal_ports

    def test_node_and_port_list(self):
        self.connection.baremetal.nodes.\
            return_value = [self.node1, self.node2]

        actual = nodes.node_and_port_list(self.connection, filter_node=None)
        expected = (
            [
                self.node1,
                self.node2
            ],
            [
                self.port1,
                self.port2,
                self.port3,
                self.port4,
            ]
        )
        self.assertEqual(expected, actual)
        self.connection.baremetal.ports.assert_called_with(details=True)

    def test_node_and_port_list_node_id_filter(self):
        actual = nodes.node_and_port_list(self.connection, filter_node='11111111-2222-3333-4444-aaaaaaaaaaaa')
        expected = (
            [
                self.node1,
            ],
            [
                self.port1,
            ]
        )
        self.assertEqual(actual, expected)
        self.connection.baremetal.ports.assert_called_with(details=True, node_id='11111111-2222-3333-4444-aaaaaaaaaaaa')


class TestNetworkList(TestCase):

    def setUp(self):
        super(TestNetworkList, self).setUp()
        self.maxDiff = None

        self.port1 = utils.create_mock_object({
            "id": "port_uuid_1",
            "node_id": "11111111-2222-3333-4444-aaaaaaaaaaaa",
            "address": "aa:aa:aa:aa:aa:aa",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_1'}
        })
        self.port2 = utils.create_mock_object({
            "id": "port_uuid_2",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "bb:bb:bb:bb:bb:bb",
            "internal_info": {}
        })
        self.port3 = utils.create_mock_object({
            "id": "port_uuid_3",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "cc:cc:cc:cc:cc:cc",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_2'}
        })
        self.port4 = utils.create_mock_object({
            "id": "port_uuid_4",
            "node_id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "address": "dd:dd:dd:dd:dd:dd",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_4'}
        })
        self.port5 = utils.create_mock_object({
            "id": "port_uuid_5",
            "node_id": "11111111-2222-3333-4444-aaaaaaaaaaaa",
            "address": "ee:ee:ee:ee:ee:ee",
            "internal_info": {'tenant_vif_port_id': 'neutron_port_uuid_3'}
        })
        self.node1 = utils.create_mock_object({
            "id": "11111111-2222-3333-4444-aaaaaaaaaaaa",
            "name": "node1"
        })
        self.node2 = utils.create_mock_object({
            "id": "11111111-2222-3333-4444-bbbbbbbbbbbb",
            "name": "node2"
        })
        self.network1 = utils.create_mock_object({
            "id": "network_uuid_1",
            "name": "test_network_1"
        })
        self.network2 = utils.create_mock_object({
            "id": "network_uuid_2",
            "name": "test_network_2"
        })
        self.network3 = utils.create_mock_object({
            "id": "network_uuid_3",
            "name": "test_network_3"
        })
        self.neutron_port1 = utils.create_mock_object({
            "id": "neutron_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "neutron_port_1",
            "fixed_ips": [{"ip_address": "1.1.1.1"}],
            "trunk_details": None
        })
        self.neutron_port2 = utils.create_mock_object({
            "id": "neutron_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "neutron_port_2",
            "fixed_ips": [{"ip_address": "2.2.2.2"}],
            "trunk_details": None
        })
        self.neutron_port3 = utils.create_mock_object({
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
        self.sub_port1 = utils.create_mock_object({
            "id": "sub_port_uuid_1",
            "network_id": "network_uuid_1",
            "name": "sub_port_1",
            "fixed_ips": [{"ip_address": "4.4.4.4"}],
            "trunk_details": None
        })
        self.sub_port2 = utils.create_mock_object({
            "id": "sub_port_uuid_2",
            "network_id": "network_uuid_2",
            "name": "sub_port_2",
            "fixed_ips": [{"ip_address": "5.5.5.5"}],
            "trunk_details": None
        })
        self.floating_network = utils.create_mock_object({
            "id": "floating_network_id",
            "name": "floating_network"
        })
        self.floating_ip = utils.create_mock_object({
            "id": "floating_ip_uuid_2",
            "floating_ip_address": "8.8.8.8",
            "floating_network_id": "floating_network_id",
            "port_id": "neutron_port_uuid_2"
        })
        self.floating_ip_pfw = utils.create_mock_object({
            "id": "floating_ip_uuid_1",
            "floating_ip_address": "9.9.9.9",
            "floating_network_id": "floating_network_id",
            "port_id": None
        })
        self.pfw1 = utils.create_mock_object({
            "internal_port": 22,
            "external_port": 22,
            "internal_port_id": "neutron_port_uuid_1"
        })
        self.pfw2 = utils.create_mock_object({
            "internal_port": 23,
            "external_port": 23,
            "internal_port_id": "neutron_port_uuid_1"
        })

        self.connection = mock.Mock()

        def mock_find_node(name_or_id=None, ignore_missing=True):
            if name_or_id == "11111111-2222-3333-4444-aaaaaaaaaaaa" or name_or_id == "node1":
                return self.node1
            elif name_or_id == "11111111-2222-3333-4444-bbbbbbbbbbbb" or name_or_id == "node2":
                return self.node2
            return None
        self.connection.baremetal.find_node.side_effect = mock_find_node

        def mock_baremetal_ports(details=False, node_id=None):
            if node_id == '11111111-2222-3333-4444-aaaaaaaaaaaa':
                return [self.port1, self.port5]
            if node_id == '11111111-2222-3333-4444-bbbbbbbbbbbb':
                return [self.port2, self.port3, self.port4]
            return [self.port1, self.port2, self.port3, self.port4, self.port5]
        self.connection.baremetal.ports.side_effect = mock_baremetal_ports

        def mock_network_ports(network_id=None):
            if network_id == 'network_uuid_1':
                return [self.neutron_port1]
            elif network_id == 'network_uuid_2':
                return [self.neutron_port2]
            if network_id == 'network_uuid_3':
                return [self.neutron_port3]
            elif network_id:
                return []
            return [self.neutron_port1, self.neutron_port2, self.neutron_port3]
        self.connection.network.ports.side_effect = mock_network_ports

        def mock_find_network(name_or_id=None, ignore_missing=True):
            if name_or_id == 'test_network_1' or name_or_id == 'network_uuid_1':
                return self.network1
            elif name_or_id == 'test_network_2' or name_or_id == 'network_uuid_2':
                return self.network2
            elif name_or_id == 'test_network_3' or name_or_id == 'network_uuid_3':
                return self.network3
            elif name_or_id == 'floating_network' or name_or_id == 'floating_network_id':
                return self.floating_network
            return None
        self.connection.network.find_network.side_effect = mock_find_network

        def mock_port_forwardings(floating_ip=None):
            if floating_ip.id == 'floating_ip_uuid_1':
                return [self.pfw1, self.pfw2]
            return []
        self.connection.network.port_forwardings.side_effect = mock_port_forwardings

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

        self.connection.baremetal.nodes.\
            return_value = [self.node1, self.node2]
        self.connection.network.networks.\
            return_value = [self.network1, self.network2, self.network3, self.floating_network]
        self.connection.network.ips.\
            return_value = [self.floating_ip, self.floating_ip_pfw]

    def test_network_list(self):
        filter_node = None
        filter_network = None
        actual = nodes.network_list(self.connection,
                                    filter_node=filter_node,
                                    filter_network=filter_network)
        expected = [
            {
                'node': self.node1,
                'network_info': [
                    {
                        'baremetal_port': self.port1,
                        'network_ports': [self.neutron_port1],
                        'networks': {
                            'parent': self.network1,
                            'trunk': [],
                            'floating': self.floating_network
                        },
                        'floating_ip': self.floating_ip_pfw,
                        'port_forwardings': [self.pfw1, self.pfw2]
                    },
                    {
                        'baremetal_port': self.port5,
                        'network_ports': [
                            self.neutron_port3,
                            self.sub_port1,
                            self.sub_port2,
                        ],
                        'networks': {
                            'parent': self.network3,
                            'trunk': [self.network1, self.network2],
                            'floating': None,
                        },
                        'floating_ip': None,
                        'port_forwardings': []
                    }
                ]
            },
            {
                'node': self.node2,
                'network_info': [
                    {
                        'baremetal_port': self.port2,
                        'network_ports': [],
                        'networks': {
                            'parent': None,
                            'trunk': [],
                            'floating': None
                        },
                        'floating_ip': None,
                        'port_forwardings': [],
                    },
                    {
                        'baremetal_port': self.port3,
                        'network_ports': [self.neutron_port2],
                        'networks': {
                            'parent': self.network2,
                            'trunk': [],
                            'floating': self.floating_network
                        },
                        'floating_ip': self.floating_ip,
                        'port_forwardings': [],
                    },
                    {
                        'baremetal_port': self.port4,
                        'network_ports': [],
                        'networks': {
                            'parent': None,
                            'trunk': [],
                            'floating': None
                        },
                        'floating_ip': None,
                        'port_forwardings': [],
                    }
                ]
            }
        ]

        self.assertEqual(actual, expected)
        self.connection.network.find_network.assert_not_called()
        self.connection.baremetal.ports.assert_called_once_with(details=True)
        self.connection.network.ports.assert_called_once_with()
        self.connection.network.port_forwardings.assert_called_once_with(floating_ip=self.floating_ip_pfw)
        self.connection.network.get_network.assert_not_called()
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_1')
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_2')

    def test_network_list_filter_node(self):
        filter_node = 'node1'
        filter_network = None
        actual = nodes.network_list(self.connection,
                                    filter_node=filter_node,
                                    filter_network=filter_network)

        expected = [
            {
                'node': self.node1,
                'network_info': [
                    {
                        'baremetal_port': self.port1,
                        'network_ports': [self.neutron_port1],
                        'networks': {
                            'parent': self.network1,
                            'trunk': [],
                            'floating': self.floating_network
                        },
                        'floating_ip': self.floating_ip_pfw,
                        'port_forwardings': [self.pfw1, self.pfw2]
                    },
                    {
                        'baremetal_port': self.port5,
                        'network_ports': [
                            self.neutron_port3,
                            self.sub_port1,
                            self.sub_port2,
                        ],
                        'networks': {
                            'parent': self.network3,
                            'trunk': [self.network1, self.network2],
                            'floating': None,
                        },
                        'floating_ip': None,
                        'port_forwardings': []
                    }
                ]
            }
        ]

        self.assertEqual(expected, actual)
        self.connection.network.find_network.assert_not_called()
        self.connection.baremetal.ports.assert_called_once_with(details=True, node_id='11111111-2222-3333-4444-aaaaaaaaaaaa')
        self.connection.network.ports.assert_called_once_with()
        self.connection.network.port_forwardings.assert_called_once_with(floating_ip=self.floating_ip_pfw)
        self.connection.network.get_network.assert_not_called()
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_1')
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_2')

    def test_network_list_filter_network(self):
        filter_node = None
        filter_network = 'test_network_3'
        actual = nodes.network_list(self.connection,
                                    filter_node=filter_node,
                                    filter_network=filter_network)

        expected = [
            {
                'node': self.node1,
                'network_info': [
                    {
                        'baremetal_port': self.port5,
                        'network_ports': [
                            self.neutron_port3,
                            self.sub_port1,
                            self.sub_port2,
                        ],
                        'networks': {
                            'parent': self.network3,
                            'trunk': [self.network1, self.network2],
                            'floating': None,
                        },
                        'floating_ip': None,
                        'port_forwardings': []
                    }
                ]
            }
        ]

        self.assertEqual(expected, actual)
        self.connection.network.find_network.assert_called_once_with(name_or_id=filter_network, ignore_missing=False)
        self.connection.baremetal.ports.assert_called_once_with(details=True)
        self.connection.network.ports.assert_called_once_with(network_id='network_uuid_3')
        self.connection.network.port_forwardings.assert_called_once_with(floating_ip=self.floating_ip_pfw)
        self.connection.network.get_network.assert_not_called()
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_1')
        self.connection.network.get_port.assert_any_call(port='sub_port_uuid_2')

    def test_network_list_filter_node_network(self):
        filter_node = '11111111-2222-3333-4444-bbbbbbbbbbbb'
        filter_network = 'network_uuid_2'
        actual = nodes.network_list(self.connection,
                                    filter_node=filter_node,
                                    filter_network=filter_network)

        expected = [
            {
                'node': self.node2,
                'network_info': [
                    {
                        'baremetal_port': self.port3,
                        'network_ports': [self.neutron_port2],
                        'networks': {
                            'parent': self.network2,
                            'trunk': [],
                            'floating': self.floating_network
                        },
                        'floating_ip': self.floating_ip,
                        'port_forwardings': [],
                    }
                ]
            }
        ]

        self.assertEqual(expected, actual)
        self.connection.network.find_network.assert_called_once_with(name_or_id=filter_network, ignore_missing=False)
        self.connection.baremetal.ports.assert_called_once_with(details=True, node_id='11111111-2222-3333-4444-bbbbbbbbbbbb')
        self.connection.network.ports.assert_called_once_with(network_id='network_uuid_2')
        self.connection.network.port_forwardings.assert_called_once_with(floating_ip=self.floating_ip_pfw)
        self.connection.network.get_port.assert_not_called()
