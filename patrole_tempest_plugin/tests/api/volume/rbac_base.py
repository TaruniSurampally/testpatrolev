# Copyright 2017 AT&T Corporation.
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

from tempest.api.volume import base as vol_base
from tempest import config
from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils

from patrole_tempest_plugin import rbac_utils

CONF = config.CONF


class BaseVolumeRbacTest(vol_base.BaseVolumeTest):

    credentials = ['admin', 'primary']

    @classmethod
    def skip_checks(cls):
        super(BaseVolumeRbacTest, cls).skip_checks()
        if not CONF.rbac.enable_rbac:
            raise cls.skipException(
                "%s skipped as RBAC testing not enabled" % cls.__name__)

    @classmethod
    def setup_clients(cls):
        super(BaseVolumeRbacTest, cls).setup_clients()
        cls.auth_provider = cls.os_primary.auth_provider

        cls.rbac_utils = rbac_utils.RbacUtils(cls)

        version_checker = {
            2: [cls.os_primary.volume_hosts_v2_client,
                cls.os_primary.volume_types_v2_client],
            3: [cls.os_primary.volume_hosts_v2_client,
                cls.os_primary.volume_types_v2_client]
        }
        cls.volume_hosts_client, cls.volume_types_client = \
            version_checker[cls._api_version]

    @classmethod
    def resource_setup(cls):
        super(BaseVolumeRbacTest, cls).resource_setup()
        cls.volume_types = []

    @classmethod
    def resource_cleanup(cls):
        super(BaseVolumeRbacTest, cls).resource_cleanup()
        cls.clear_volume_types()

    @classmethod
    def create_volume_type(cls, name=None, **kwargs):
        """Create a test volume-type"""
        name = name or data_utils.rand_name(cls.__name__ + '-volume-type')
        volume_type = cls.volume_types_client.create_volume_type(
            name=name, **kwargs)['volume_type']
        cls.volume_types.append(volume_type['id'])
        return volume_type

    @classmethod
    def clear_volume_types(cls):
        for vol_type in cls.volume_types:
            test_utils.call_and_ignore_notfound_exc(
                cls.volume_types_client.delete_volume_type, vol_type)

        for vol_type in cls.volume_types:
            test_utils.call_and_ignore_notfound_exc(
                cls.volume_types_client.wait_for_resource_deletion, vol_type)
