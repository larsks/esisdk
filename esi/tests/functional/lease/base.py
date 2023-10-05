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

from esi import connection

from openstack.tests.functional import base


class BaseESILEAPTest(base.BaseFunctionalTest):
    min_microversion = None

    def require_service(service_type, min_microversion=None, **kwargs):
        pass

    def setUp(self):
        super(BaseESILEAPTest, self).setUp()
        self.conn = connection.ESIConnection(config=base.TEST_CLOUD_REGION)

    def create_offer(self, node_id=None, node_type=None, **kwargs):
        offer = self.conn.lease.create_offer(resource_id=node_id,
                                             node_type=node_type,
                                             **kwargs)
        self.addCleanup(
            lambda: self.conn.lease.delete_offer(
                offer.id, ignore_missing=True
            )
        )
        return offer

    def create_lease(self, node_id=None, project_id=None, **kwargs):
        lease = self.conn.lease.create_lease(resource_id=node_id,
                                             project_id=project_id,
                                             **kwargs)
        self.addCleanup(
            lambda: self.conn.lease.delete_lease(
                lease.id, ignore_missing=True
            )
        )
        return lease
