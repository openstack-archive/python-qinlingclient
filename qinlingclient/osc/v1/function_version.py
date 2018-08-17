# Copyright 2017 Catalyst IT Limited
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from osc_lib.command import command
from osc_lib import utils
from oslo_utils import uuidutils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient import utils as q_utils


class List(base.QinlingLister):
    columns = base.FUNCTION_VERSION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(List, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )

        return parser

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.function_versions.list(parsed_args.function_id)


class Create(command.ShowOne):
    columns = base.FUNCTION_VERSION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "function",
            help="Function name or ID.",
        )
        parser.add_argument(
            "--description",
            help="Description for the new version.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        function_id = parsed_args.function
        if not uuidutils.is_uuid_like(function_id):
            # Try to find the function id with name
            function_id = q_utils.find_resource_id_by_name(
                client.functions, function_id)

        version = client.function_versions.create(
            function_id,
            description=parsed_args.description,
        )

        return self.columns, utils.get_item_properties(version, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )
        parser.add_argument(
            "version_number",
            help="Function version.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        client.function_versions.delete(parsed_args.function_id,
                                        parsed_args.version_number)


class Show(command.ShowOne):
    columns = base.FUNCTION_VERSION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )
        parser.add_argument(
            "version_number",
            help="Function version.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        version = client.function_versions.get(parsed_args.function_id,
                                               parsed_args.version_number)

        return self.columns, utils.get_item_properties(version, self.columns)


class Detach(command.Command):
    def get_parser(self, prog_name):
        parser = super(Detach, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )
        parser.add_argument(
            "version_number",
            help="Function version.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        success_msg = "Request to detach function %s(version %s) has been " \
                      "accepted."
        error_msg = "Unable to detach the specified function version."

        try:
            client.function_versions.detach(parsed_args.function_id,
                                            parsed_args.version_number)
            print(
                success_msg %
                (parsed_args.function_id, parsed_args.version_number)
            )
        except Exception as e:
            print(e)
            raise exceptions.QinlingClientException(error_msg)
