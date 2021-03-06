#    Copyright 2017 AT&T Corporation.
#    All Rights Reserved.
#
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

from tempest.lib.common.utils import data_utils
from tempest.lib.common.utils import test_utils
from tempest.lib import decorators
from tempest import test

from patrole_tempest_plugin import rbac_rule_validation
from patrole_tempest_plugin.tests.api.compute import rbac_base


class QuotaSetsRbacTest(rbac_base.BaseV2ComputeRbacTest):

    @classmethod
    def setup_clients(cls):
        super(QuotaSetsRbacTest, cls).setup_clients()
        cls.projects_client = cls.os_primary.projects_client

    @classmethod
    def skip_checks(cls):
        super(QuotaSetsRbacTest, cls).skip_checks()
        if not test.is_extension_enabled('os-quota-sets', 'compute'):
            msg = "%s skipped as quotas extension not enabled."\
                  % cls.__name__
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        super(QuotaSetsRbacTest, cls).resource_setup()
        cls.tenant_id = cls.quotas_client.tenant_id
        cls.user_id = cls.quotas_client.user_id
        cls.quota_set = set(('injected_file_content_bytes',
                             'metadata_items', 'injected_files',
                             'ram', 'floating_ips', 'fixed_ips', 'key_pair',
                             'injected_file_path_bytes', 'instances',
                             'security_group_rules', 'cores',
                             'security_groups'))

    @decorators.idempotent_id('8229ceb0-db6a-4a2c-99c2-de226905d8b6')
    @rbac_rule_validation.action(
        service="nova",
        rule="os_compute_api:os-quota-sets:update")
    def test_update_quota_set(self):
        default_quota_set = self.quotas_client.show_default_quota_set(
            self.tenant_id)['quota_set']
        default_quota_set.pop('id')
        new_quota_set = {'injected_file_content_bytes': 20480}

        self.rbac_utils.switch_role(self, toggle_rbac_role=True)
        self.quotas_client.update_quota_set(self.tenant_id,
                                            force=True,
                                            **new_quota_set)['quota_set']
        self.addCleanup(self.quotas_client.update_quota_set, self.tenant_id,
                        **default_quota_set)

    @decorators.idempotent_id('58df5613-8f3c-400a-8b4b-2bae624d05e9')
    @rbac_rule_validation.action(
        service="nova",
        rule="os_compute_api:os-quota-sets:defaults")
    def test_show_default_quota_set(self):
        self.rbac_utils.switch_role(self, toggle_rbac_role=True)
        self.quotas_client.show_default_quota_set(self.tenant_id)['quota_set']

    @decorators.idempotent_id('e8169ac4-c402-4864-894e-aba74e3a459c')
    @rbac_rule_validation.action(
        service="nova",
        rule="os_compute_api:os-quota-sets:show")
    def test_show_quota_set(self):
        self.rbac_utils.switch_role(self, toggle_rbac_role=True)
        self.quotas_client.show_quota_set(self.tenant_id)['quota_set']

    @decorators.idempotent_id('4e240644-bf61-4872-9c32-8289ee2fdbbd')
    @rbac_rule_validation.action(
        service="nova",
        rule="os_compute_api:os-quota-sets:delete")
    def test_delete_quota_set(self):
        project_name = data_utils.rand_name(
            self.__class__.__name__ + '-project')
        project = self.projects_client.create_project(name=project_name)
        project_id = project['project']['id']
        self.addCleanup(test_utils.call_and_ignore_notfound_exc,
                        self.projects_client.delete_project, project_id)

        self.rbac_utils.switch_role(self, toggle_rbac_role=True)
        self.quotas_client.delete_quota_set(project_id)

    @decorators.idempotent_id('ac9184b6-f3b3-4e17-a632-4b92c6500f86')
    @rbac_rule_validation.action(
        service="nova",
        rule="os_compute_api:os-quota-sets:detail")
    def test_show_quota_set_details(self):
        self.rbac_utils.switch_role(self, toggle_rbac_role=True)
        self.quotas_client.show_quota_set(self.tenant_id,
                                          detail=True)['quota_set']
