# esisdk

Unified SDK for ESI

## Install ESI SDK:

```
python setup.py install
```

## Create a connection to ESI SDK

There are several methods to establish a connection using the ESI SDK. Since the `esi.connection.ESIConnection` class inherits from `openstack.connection.Connection`, [methods applicable for creating connections](https://docs.openstack.org/openstacksdk/latest/user/connection.html)
in the OpenStack SDK can also be used with the ESI SDK. Below are some common ways to create an `ESIConnection`:

### Create a connection using only keyword arguments

```
from esi import connection

conn = connection.ESIConnection(
    region_name='example-region',
    auth={
        'auth_url': 'https://auth.example.com',
        'username': 'user',
        'password': 'password',
        'project_name': 'project_name',
        'user_domain_name': 'user_domain_name',
        'project_domain_name': 'project_domain_name'
    },
    interface='public'
)
```

### Create a connection from existing CloudRegion

```
from esi import connection
import openstack.config

config = openstack.config.get_cloud_region(
    cloud='example',
    region_name='earth'
)
conn = connection.ESIConnectionn(config=config)
```

## Make API calls

Detailed APIs can be found in the  `esi/lease/v1/_proxy.py` file. Below are simple examples demonstrating lease resource CRUD operations.

```
import esi
import os

TEST_CLOUD = os.getenv('OS_TEST_CLOUD', 'devstack-admin')
conn = esi.connect(cloud=TEST_CLOUD)

# Create a lease
def lease_create(conn, resource_uuid, project_id, **kwargs):
    lease = conn.lease.create_lease(resource_uuid=resource_uuid,
                                    project_id=project_id,
                                    **kwargs)

# List leases
def lease_list(conn, **kwargs):
    leases = conn.lease.leases(**kwargs)

# Update a lease
def lease_update(conn, lease, **kwargs):
    lease_dict = conn.lease.update_lease(lease, **kwargs)

# Delete a lease
def lease_delete(conn, lease_id):
    leases = conn.lease.delete_lease(lease_id)
```
