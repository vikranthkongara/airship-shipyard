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

import json
import logging
import os
import requests

from airflow.plugins_manager import AirflowPlugin
from airflow.exceptions import AirflowException

from drydock_base_operator import DrydockBaseOperator


class DrydockValidateDesignOperator(DrydockBaseOperator):

    """Drydock Validate Design Operator

    This operator will trigger drydock to validate the
    site design

    """

    def do_execute(self):

        # Form Validation Endpoint
        validation_endpoint = os.path.join(self.drydock_svc_endpoint,
                                           'validatedesign')

        logging.info("Validation Endpoint is %s", validation_endpoint)

        # Define Headers and Payload
        headers = {
            'Content-Type': 'application/json',
            'X-Auth-Token': self.svc_token
        }

        payload = {
            'rel': "design",
            'href': self.deckhand_design_ref,
            'type': "application/x-yaml"
        }

        # Requests DryDock to validate site design
        logging.info("Waiting for DryDock to validate site design...")

        try:
            design_validate_response = requests.post(validation_endpoint,
                                                     headers=headers,
                                                     data=json.dumps(payload))

        except requests.exceptions.RequestException as e:
            raise AirflowException(e)

        # Convert response to string
        validate_site_design = design_validate_response.text

        # Print response
        logging.info("Retrieving DryDock validate site design response...")
        logging.info(json.loads(validate_site_design))

        # Check if site design is valid
        if json.loads(validate_site_design).get('status') == 'Success':
            logging.info("DryDock Site Design has been successfully validated")
        else:
            raise AirflowException("DryDock Site Design Validation Failed!")


class DrydockValidateDesignOperatorPlugin(AirflowPlugin):

    """Creates DrydockValidateDesignOperator in Airflow."""

    name = 'drydock_validate_design_operator'
    operators = [DrydockValidateDesignOperator]