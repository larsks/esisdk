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

from esi.lease.v1._proxy import Proxy


class LeaseCloudMixin:
    lease: Proxy

    def __init__(self):
        super(LeaseCloudMixin, self).__init__()
        self.cache_enabled = False

    def list_offers(self, **kwargs):
        """Return a list of all offers."""
        return list(self.lease.offers(**kwargs))

    def create_offer(self, resource_id, node_type, **kwargs):
        """Create an offer"""
        return self.lease.create_offer(resource_id=resource_id,
                                       node_type=node_type,
                                       **kwargs)

    def delete_offer(self, offer):
        """Delete an offer"""
        return self.lease.delete_offer(offer)

    def claim_offer(self, offer, **kwargs):
        """Claim an offer"""
        return self.lease.claim_offer(offer, **kwargs)

    def list_leases(self, **kwargs):
        """Return a list of all leases"""
        return list(self.lease.leases(**kwargs))

    def create_lease(self, resource_id, project_id, **kwargs):
        """Create a lease"""
        return self.lease.create_lease(resource_id=resource_id,
                                       project_id=project_id,
                                       **kwargs)

    def delete_lease(self, lease):
        """Delete a lease"""
        return self.lease.delete_lease(lease)

    def list_nodes(self):
        """Return a list of all nodes info"""
        return list(self.lease.nodes())

    def list_events(self, **kwargs):
        """Return a list of events"""
        return list(self.lease.events(**kwargs))
