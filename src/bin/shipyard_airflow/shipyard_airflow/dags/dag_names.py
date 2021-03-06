# Copyright 2018 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Subdags
ALL_PREFLIGHT_CHECKS_DAG_NAME = 'preflight'
ARMADA_BUILD_DAG_NAME = 'armada_build'
DESTROY_SERVER_DAG_NAME = 'destroy_server'
DRYDOCK_BUILD_DAG_NAME = 'drydock_build'
VALIDATE_SITE_DESIGN_DAG_NAME = 'validate_site_design'

# Steps
ACTION_XCOM = 'action_xcom'
CONCURRENCY_CHECK = 'dag_concurrency_check'
CREATE_ACTION_TAG = 'create_action_tag'
DECIDE_AIRFLOW_UPGRADE = 'decide_airflow_upgrade'
DEPLOYMENT_CONFIGURATION = 'deployment_configuration'
GET_RENDERED_DOC = 'get_rendered_doc'
SKIP_UPGRADE_AIRFLOW = 'skip_upgrade_airflow'
UPGRADE_AIRFLOW = 'upgrade_airflow'
