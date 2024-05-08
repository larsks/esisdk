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

"""
fakes
-----

Fakes used for testing
"""

from keystoneauth1 import discover as ks_discover
from openstack.cloud import meta


class FakeOffer:
    def __init__(self, id, node_id, node_type):
        self.id = id
        self.resource_uuid = node_id
        self.node_type = node_type


class FakeLease:
    def __init__(self, id, node_id, node_type, offer_uuid):
        self.id = id
        self.resource_uuid = node_id
        self.node_type = node_type
        self.offer_uuid = offer_uuid


class FakeNode:
    def __init__(self, id, offer_uuid, lease_uuid):
        self.id = id
        self.offer_uuid = offer_uuid
        self.lease_uuid = lease_uuid


class FakeEvent:
    def __init__(self, id, event_type, last_event_time):
        self.id = id
        self.event_type = event_type
        self.last_event_time = last_event_time


def make_fake_offer(id, node_id, node_type):
    return meta.obj_to_munch(FakeOffer(id=id,
                                       node_id=node_id,
                                       node_type=node_type))


def make_fake_lease(id, node_id, node_type, offer_uuid):
    return meta.obj_to_munch(FakeLease(id=id,
                                       node_id=node_id,
                                       node_type=node_type,
                                       offer_uuid=offer_uuid))


def make_fake_node(id, offer_uuid, lease_uuid):
    return meta.obj_to_munch(FakeNode(id=id,
                                      offer_uuid=offer_uuid,
                                      lease_uuid=lease_uuid))


def make_fake_event(id, event_type, last_event_time):
    return meta.obj_to_munch(FakeEvent(id=id,
                                       event_type=event_type,
                                       last_event_time=last_event_time))


def get_lease_endpoint():
    url = "https://lease.example.com"
    return ks_discover.EndpointData(catalog_url=url, api_version=(1, 0))
