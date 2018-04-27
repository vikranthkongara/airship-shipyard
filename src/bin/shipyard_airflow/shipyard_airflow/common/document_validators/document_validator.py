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
"""Base class for document validators"""
import abc
import logging

from .errors import (
    DeckhandClientRequiredError, DocumentLookupError, DocumentNotFoundError
)
from .document_validation_utils import DocumentValidationUtils

LOG = logging.getLogger(__name__)


class DocumentValidator(metaclass=abc.ABCMeta):
    """Document validator base class

    :param deckhand_client: An instance of a Deckhand client that can be used
        to interact with Deckhand during the validation
    :param revision: The numeric Deckhand revision of document under test
    :param doc_name: The name of the document under test
    """
    def __init__(self, deckhand_client, revision, doc_name):
        if deckhand_client is None:
            raise DeckhandClientRequiredError()
        self.deckhand_client = deckhand_client
        self.docutils = DocumentValidationUtils(self.deckhand_client)
        self.doc_name = doc_name

        # self.error_status is False if no validations fail. It becomes
        # True for any validatoion failure (including missing docs that are
        # not error level, because it interrupts the flow from proceeding with
        # further validation.)
        self.error_status = False
        self.revision = revision
        self._triggered_validations = []
        self.val_msg_list = []

    @property
    @abc.abstractmethod
    def schema(self):
        """The schema name of the document being validated by this validator"""
        pass

    @property
    @abc.abstractmethod
    def missing_severity(self):
        """The severity level if this document is missing

        Error, Warning, or Info
        """
        pass

    @property
    def triggered_validations(self):
        return self._triggered_validations

    def add_triggered_validation(self, validator_class, doc_name):
        """The validation to add to the list of triggered validations

        :param validator_class: The class of the validator to use
        :param doc_name: the document name to validate
        """
        self._triggered_validations.append((validator_class, doc_name))

    def val_msg(self, message, name, error=True, level='Error',
                documents=None, diagnostic=None):
        """Generate a ValidationMessage

        :param error: True or False
        :param level: "Error", "Warning", "Info"
        :param message: The explanation of the valiadaiton message
        :param name: The short name of the messge, e.g.: DocumentMissing
        :param documents: list of {"schema": <schema name>,
                                   "name": <document name>}
            defaults to the current document under test
        :param diagnostic: Possible solutions or troubleshooting. Defaults to
            a generic message about being generated by Shipyard
        In accordance with:
        https://github.com/att-comdev/ucp-integration/blob/master/docs/source/api-conventions.rst#validationmessage-message-type
        """
        if documents is None:
            documents = [{"schema": self.schema, "name": self.doc_name}]

        if diagnostic is None:
            diagnostic = "Message generated by Shipyard."

        return {
            "error": error,
            "level": level,
            "message": message,
            "name": name,
            "documents": documents,
            "diagnostic": diagnostic,
            "kind": "ValidationMessage"
        }

    @abc.abstractmethod
    def do_validate(self):
        """Run Validations"""
        pass

    def validate(self):
        """Triggers the validations for this validator

        Triggers the specific checks after any common checks
        """
        if self.missing_severity not in ["Error", "Warning", "Info"]:
            LOG.warn("Document Validator for {}, {} does not have a valid "
                     "value set for missing_severity. Assuming Error".format(
                         self.schema, self.doc_name
                     ))
            self.missing_severity = "Error"

        try:
            LOG.debug("Lookup up document %s: %s from revision %s",
                      self.schema,
                      self.doc_name,
                      self.revision)
            self.doc_dict = self.docutils.get_unique_doc(self.revision,
                                                         self.doc_name,
                                                         self.schema)
            # only proceed to validating the document if it is present.
            LOG.debug("Generic document validaton complete. Proceeding to "
                      "specific validation")
            self.do_validate()
        except DocumentLookupError as dle:
            self.val_msg_list.append(self.val_msg(
                name=dle.__class__.__name__,
                error=True,
                level="Error",
                message="Document Lookup failed for {}".format(self.schema),
                diagnostic=str(dle)))
        except DocumentNotFoundError as dnfe:
            name = dnfe.__class__.__name__

            if self.missing_severity == "Error":
                diagnostic = (
                    "The configuration documents must include a document with "
                    "schema: {} and name: {}".format(
                        self.schema,
                        self.doc_name
                    )
                )
                message = "Missing required document {}".format(self.schema)
                error = True
                self.error_status = True
            elif self.missing_severity == "Warning":
                diagnostic = (
                    "It is recommended, but not required that the "
                    "configuration documents include a document with "
                    "schema: {} and name: {}".format(
                        self.schema,
                        self.doc_name
                    )
                )
                message = "Missing recommended document {}".format(self.schema)
                error = False
                self.error_status = True
            elif self.missing_severity == "Info":
                diagnostic = (
                    "Optional document with schema: {} and name: {} was not"
                    "found among the configuration documents.".format(
                        self.schema,
                        self.doc_name
                    )
                )
                message = "Optional document {} not found".format(self.schema)
                error = False
                self.error_status = True

            self.val_msg_list.append(self.val_msg(
                name=name, error=error, level=self.missing_severity,
                message=message, diagnostic=diagnostic
            ))
