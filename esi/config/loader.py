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

import copy
from esi.config import _util
from esi import exceptions

FORMAT_EXCLUSIONS = frozenset(['password'])


def _auth_update(old_dict, new_dict_source):
    """Like dict.update, except handling the nested dict called auth."""
    new_dict = copy.deepcopy(new_dict_source)
    for k, v in new_dict.items():
        if k == 'auth':
            if k in old_dict:
                old_dict[k].update(v)
            else:
                old_dict[k] = v.copy()
        else:
            old_dict[k] = v
    return old_dict


class ESIConfig:
    def __init__(self,
                 config_files=None,
                 vendor_files=None,
                 secure_files=None):
        self.config_files = config_files
        self.vendor_files = vendor_files
        self.secure_files = secure_files

    def _fix_args(self, args=None, argparse=None):
        """Massage the passed-in options

        Replace - with _ and strip os_ prefixes.

        Convert an argparse Namespace object to a dict, removing values
        that are either None or ''.
        """
        if not args:
            args = {}

        if argparse:
            # Convert the passed-in Namespace
            o_dict = vars(argparse)
            parsed_args = dict()
            for k in o_dict:
                if o_dict[k] is not None and o_dict[k] != '':
                    parsed_args[k] = o_dict[k]
            args.update(parsed_args)

        os_args = dict()
        new_args = dict()
        for key, val in iter(args.items()):
            if type(args[key]) == dict:
                # dive into the auth dict
                new_args[key] = self._fix_args(args[key])
                continue

            key = key.replace('-', '_')
            if key.startswith('os_'):
                os_args[key[3:]] = val
            else:
                new_args[key] = val
        new_args.update(os_args)
        return new_args

    def _get_base_cloud_config(self, name, profile=None):
        cloud = dict()

        # Only validate cloud name if one was given
        if name and name not in self.cloud_config['clouds']:
            raise exceptions.ConfigException(
                "Cloud {name} was not found.".format(name=name)
            )

        our_cloud = self.cloud_config['clouds'].get(name, dict())
        if profile:
            our_cloud['profile'] = profile

        # Get the defaults
        cloud.update(self.defaults)
        self._expand_vendor_profile(name, cloud, our_cloud)

        if 'auth' not in cloud:
            cloud['auth'] = dict()

        _auth_update(cloud, our_cloud)
        if 'cloud' in cloud:
            del cloud['cloud']

        return cloud

    def get_one(self, cloud=None, validate=True, argparse=None, **kwargs):
        """Retrieve a single CloudRegion and merge additional options

        :param string cloud:
            The name of the configuration to load from clouds.yaml
        :param boolean validate:
            Validate the config. Setting this to False causes no auth plugin
            to be created. It's really only useful for testing.
        :param Namespace argparse:
            An argparse Namespace object; allows direct passing in of
            argparse options to be added to the cloud config.  Values
            of None and '' will be removed.
        :param region_name: Name of the region of the cloud.
        :param kwargs: Additional configuration options

        :returns: openstack.config.cloud_region.CloudRegion
        :raises: keystoneauth1.exceptions.MissingRequiredOptions
            on missing required auth parameters
        """

        profile = kwargs.pop('profile', None)
        args = self._fix_args(kwargs, argparse=argparse)

        if cloud is None:
            if 'cloud' in args:
                cloud = args['cloud']
            else:
                cloud = self.default_cloud

        config = self._get_base_cloud_config(cloud, profile)

        # Get region specific settings
        if 'region_name' not in args:
            args['region_name'] = ''
        region = self._get_region(cloud=cloud, region_name=args['region_name'])
        args['region_name'] = region['name']
        region_args = copy.deepcopy(region['values'])

        # Regions is a list that we can use to create a list of cloud/region
        # objects. It does not belong in the single-cloud dict
        config.pop('regions', None)

        # Can't just do update, because None values take over
        for arg_list in region_args, args:
            for key, val in iter(arg_list.items()):
                if val is not None:
                    if key == 'auth' and config[key] is not None:
                        config[key] = _auth_update(config[key], val)
                    else:
                        config[key] = val

        config = self.magic_fixes(config)
        config = _util.normalize_keys(config)

        # NOTE(dtroyer): OSC needs a hook into the auth args before the
        #                plugin is loaded in order to maintain backward-
        #                compatible behaviour
        config = self.auth_config_hook(config)

        if validate:
            loader = self._get_auth_loader(config)
            config = self._validate_auth(config, loader)
            auth_plugin = loader.load_from_options(**config['auth'])
        else:
            auth_plugin = None

        # If any of the defaults reference other values, we need to expand
        for key, value in config.items():
            if hasattr(value, 'format') and key not in FORMAT_EXCLUSIONS:
                config[key] = value.format(**config)

        force_ipv4 = config.pop('force_ipv4', self.force_ipv4)
        prefer_ipv6 = config.pop('prefer_ipv6', True)
        if not prefer_ipv6:
            force_ipv4 = True

        # Override global metrics config with more specific per-cloud
        # details.
        metrics_config = config.get('metrics', {})
        statsd_config = metrics_config.get('statsd', {})
        statsd_host = statsd_config.get('host') or self._statsd_host
        statsd_port = statsd_config.get('port') or self._statsd_port
        statsd_prefix = statsd_config.get('prefix') or self._statsd_prefix
        influxdb_config = metrics_config.get('influxdb', {})
        if influxdb_config:
            merged_influxdb = copy.deepcopy(self._influxdb_config)
            merged_influxdb.update(influxdb_config)
            influxdb_config = merged_influxdb
        else:
            influxdb_config = self._influxdb_config

        if cloud is None:
            cloud_name = ''
        else:
            cloud_name = str(cloud)
        return self._cloud_region_class(
            name=cloud_name,
            region_name=config['region_name'],
            config=config,
            extra_config=self.extra_config,
            force_ipv4=force_ipv4,
            auth_plugin=auth_plugin,
            openstack_config=self,
            session_constructor=self._session_constructor,
            app_name=self._app_name,
            app_version=self._app_version,
            cache_auth=self._cache_auth,
            cache_expiration_time=self._cache_expiration_time,
            cache_expirations=self._cache_expirations,
            cache_path=self._cache_path,
            cache_class=self._cache_class,
            cache_arguments=self._cache_arguments,
            password_callback=self._pw_callback,
            statsd_host=statsd_host,
            statsd_port=statsd_port,
            statsd_prefix=statsd_prefix,
            influxdb_config=influxdb_config,
        )

    # TODO(mordred) Backwards compat for OSC transition
    get_one_cloud = get_one
