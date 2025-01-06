### Prerequisites

These tests are intended to be run against a functioning OpenStack cloud with esi-leap services enabled and running (https://github.com/CCI-MOC/esi-leap). Please set the following environment variables in order to run full tests:
* TestESILEAPLease and TestESILEAPOffer: set `NODE_1_UUID`, `NODE_1_TYPE`, `NODE_2_UUID`, `NODE_2_TYPE` in tox.ini.  These nodes should not be associated with any existing leases/offers during testing.
* TestESILEAPEvent: set `LAST_EVENT_ID`, `NODE_1_UUID` and `NODE_1_TYPE` in tox.ini.
* TestESILEAPNode: set `NODE_3_NAME` in tox.ini. This node should be associated with leases/offers.

The clouds.yaml file should be like this: https://github.com/openstack/openstacksdk/blob/master/doc/source/contributor/clouds.yaml

### Running the tests

By default, the functional tests will not run when invoking `tox` with no additional options. To run them, you must specify the 'functional' testenv like this:

```
$ tox -e functional
```

To run specific tests,
```
$ tox -e functional -- "test_node_list"
```
or
```
$ tox -e functional -- "TestESILEAPOffer"
```
