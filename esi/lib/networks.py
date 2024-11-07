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


def get_ports(connection, filter_network=None):
    if filter_network:
        neutron_ports = connection.network.ports(network_id=filter_network.id)
    else:
        neutron_ports = connection.network.ports()
    return neutron_ports


def network_and_port_list(connection, filter_network=None):
    """Gets accessible networking information

    :param connection: An OpenStack connection
    :type connection: :class:`~openstack.connection.Connection`
    :param filter_network: The name or ID of a network

    :returns: A tuple of network ports, networks, floating ips, and port forwardings of the form:
    (
        [openstack.network.v2.port.Port],
        {openstack.network.v2.network.Network.id: openstack.network.v2.network.Network},
        {openstack.network.v2.port.Port.id: openstack.network.v2.floating_ip.FloatingIP},
        {openstack.network.v2.port.Port.id: openstack.network.v2.port_forwarding.PortForwarding}
    )
    """

    floating_ips_dict = {}
    port_forwardings_dict = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        f1 = executor.submit(get_ports, connection, filter_network)
        f2 = executor.submit(connection.network.networks)
        f3 = executor.submit(connection.network.ips)
        network_ports = list(f1.result())
        networks_dict = {network.id: network for network in list(f2.result())}
        floating_ips = list(f3.result())

    for floating_ip in floating_ips:
        # no need to do this for floating IPs associated with a port,
        # as port forwarding is irrelevant in such a case
        if not floating_ip.port_id:
            pfwds = list(connection.network.port_forwardings(floating_ip=floating_ip))
            if len(pfwds):
                floating_ip.port_id = pfwds[0].internal_port_id
                port_forwardings_dict[floating_ip.port_id] = pfwds
        floating_ips_dict[floating_ip.port_id] = floating_ip

    return network_ports, networks_dict, floating_ips_dict, port_forwardings_dict


def get_networks_from_port(connection, port, networks_dict={}, floating_ips_dict={}):
    """Gets associated network objects from a port object

    :param connection: An OpenStack connection
    :type connection: :class:`~openstack.connection.Connection`
    :param port: A network port
    :type port: :class:`~openstack.network.v2.port.Port`
    :param networks_dict: A dictionary mapping network IDs to network objects
    :param floating_ips_dict: A dictionary mapping port IDs to floating IPs

    :returns: A tuple containing the parent network, trunk networks, trunk ports,
              and the floating network associated with the given port
    """

    parent_network = None
    trunk_networks = []
    trunk_ports = []

    if port.network_id in networks_dict:
        parent_network = networks_dict[port.network_id]
    else:
        parent_network = connection.network.get_network(network=port.network_id)

    if port.trunk_details:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            subport_futures = []
            subport_infos = port.trunk_details['sub_ports']
            for subport_info in subport_infos:
                subport_futures.append(executor.submit(
                    connection.network.get_port,
                    port=subport_info['port_id']
                ))
            for subport_future in subport_futures:
                subport = subport_future.result()
                if subport.network_id in networks_dict:
                    trunk_network = networks_dict[subport.network_id]
                else:
                    trunk_network = connection.network.get_network(subport.network_id)
                trunk_ports.append(subport)
                trunk_networks.append(trunk_network)

    floating_network_id = getattr(floating_ips_dict.get(port.id),
                                  'floating_network_id', None)
    if floating_network_id is None:
        floating_network = None
    elif networks_dict.get(floating_network_id):
        floating_network = networks_dict[floating_network_id]
    else:
        floating_network = connection.network.get_network(floating_network_id)

    return parent_network, trunk_networks, trunk_ports, floating_network


def create_port(connection, node_name, network):
    """
    Creates a port on the specified network using the network object.

    :param connection: An OpenStack connection object used to interact with OpenStack services.
    :param node_name: The name of the node associated with the port.
    :param network: The network object where the port should be created.
                    This object must have 'id' and 'name' attributes.

    :return: The created port object, or an existing port if a matching one was found.
    """

    port_name = 'esi-{0}-{1}'.format(node_name, network.name)
    existing_ports = list(connection.network.ports(name=port_name, status='DOWN'))

    if existing_ports:
        network_port = existing_ports[0]
    else:
        network_port = connection.network.create_port(name=port_name, network_id=network.id, device_owner='baremetal:none')

    return network_port
