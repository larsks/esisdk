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

import os

from esi.tests.functional.lease import base


class TestESILEAPNode(base.BaseESILEAPTest):
    def setUp(self):
        super(TestESILEAPNode, self).setUp()

    def test_node_list(self):
        """ Tests functionality "esi node list" using node_uuid or node name.
            checks node_uuid or node_name is present in node list or not.
            Test steps:
            1) Set the environment variables using
               export NODE_3_NAME=node_name
            2) Checks that the output of "node list" contains
               the node uuid or node name it's tested with. """

        node_name = os.getenv('NODE_3_NAME')
        nodes = self.conn.lease.nodes()

        self.assertNotEqual(nodes, [])
        if node_name is not None:
            self.assertIn(node_name, [x.name for x in nodes])
