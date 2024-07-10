
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

import concurrent.futures

from esi.lib import networks


def node_and_port_list(connection, filter_node=None):
    """Get lists baremetal nodes and ports

    :param connection: An OpenStack connection
    :type connection: :class:`~openstack.connection.Connection`
    :param filter_node: The name or ID of a node

    :returns: A tuple of lists of nodes and ports of the form:
    (
        [openstack.baremetal.v1.node.Node],
        [openstack.baremetal.v1.port.Port]
    )
    """

    nodes = None
    ports = None

    if filter_node:
        nodes = [connection.baremetal.find_node(name_or_id=filter_node,
                                                ignore_missing=False)]
        ports = connection.baremetal.ports(details=True, node_id=nodes[0].id)
    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            f1 = executor.submit(connection.baremetal.nodes)
            f2 = executor.submit(connection.baremetal.ports, details=True)
            nodes = list(f1.result())
            ports = list(f2.result())

    return nodes, ports


def network_list(connection, filter_node=None, filter_network=None):
    """List nodes and their network attributes

    :param connection: An OpenStack connection
    :type connection: :class:`~openstack.connection.Connection`
    :param filter_node: the name or ID of a node
    :param filter_network: The name or ID of a network

    :returns: A list of dictionaries of the form:
    {
        'node': openstack.baremetal.v1.node.Node,
        'network_info': [
            {
                'baremetal_port': openstack.baremetal.v1.port.Port,
                'network_ports': [openstack.network.v2.port.Port] or [],
                'networks': {
                    'parent': openstack.network.v2.network.Network or None,
                    'trunk': [openstack.network.v2.network.Network] or [],
                    'floating': openstack.network.v2.network.Network or None,
                },
                'floating_ip': openstack.network.v2.floating_ip.FloatingIP or None,
                'port_forwardings': [openstack.network.v2.port_forwarding.PortForwarding] or []
            },
            ...
        ]
    }
    """

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(node_and_port_list, connection, filter_node)
        if filter_network:
            f3 = executor.submit(connection.network.find_network,
                                 name_or_id=filter_network,
                                 ignore_missing=False)
            filter_network = f3.result()
        f2 = executor.submit(networks.network_and_port_list, connection, filter_network)
        baremetal_nodes, baremetal_ports = f1.result()
        network_ports, networks_dict, floating_ips_dict, port_forwardings_dict = f2.result()

    data = []
    for baremetal_node in baremetal_nodes:
        network_info = []
        node_ports = [bp for bp in baremetal_ports
                      if bp.node_id == baremetal_node.id]

        for baremetal_port in node_ports:
            network_port = None
            network_port_id = baremetal_port.internal_info.get('tenant_vif_port_id', None)

            if network_port_id:
                network_port = next((np for np in network_ports
                                     if np.id == network_port_id), None)

            if network_port is not None and (not filter_network or filter_network.id == network_port.network_id):
                parent_network, trunk_networks, trunk_ports, floating_network \
                    = networks.get_networks_from_port(connection,
                                                      network_port,
                                                      networks_dict,
                                                      floating_ips_dict)

                network_info.append({
                    'baremetal_port': baremetal_port,
                    'network_ports': [network_port] + trunk_ports,
                    'networks': {
                        'parent': parent_network,
                        'trunk': trunk_networks,
                        'floating': floating_network
                    },
                    'floating_ip': floating_ips_dict.get(network_port.id, None),
                    'port_forwardings': port_forwardings_dict.get(network_port.id, []),
                })
            elif not filter_network:
                network_info.append({
                    'baremetal_port': baremetal_port,
                    'network_ports': [],
                    'networks': {
                        'parent': None,
                        'trunk': [],
                        'floating': None
                    },
                    'floating_ip': None,
                    'port_forwardings': [],
                })

        if network_info != []:
            data.append({
                'node': baremetal_node,
                'network_info': network_info
            })

    return data
