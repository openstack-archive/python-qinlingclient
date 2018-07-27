# Copyright 2018 OpenStack Foundation.
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

from qinlingclient.osc.v1 import base
from qinlingclient import utils as q_utils


class List(base.QinlingLister):
    columns = base.FUNCTION_ALIAS_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.function_aliases.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.FUNCTION_ALIAS_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "name",
            help="Function Alias name.",
        )
        parser.add_argument(
            "--function",
            required=True,
            help="Function ID or Name.",
        )
        parser.add_argument(
            "--function-version",
            type=int,
            default=0,
            help="Function Version number.",
        )
        parser.add_argument(
            "--description",
            default='',
            help="Description for the new alias.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        function_id = parsed_args.function
        if not uuidutils.is_uuid_like(function_id):
            # Try to find the function id with name
            function_id = q_utils.find_resource_id_by_name(
                client.functions, function_id)

        alias = client.function_aliases.create(
            parsed_args.name,
            function_id=function_id,
            function_version=parsed_args.function_version,
            description=parsed_args.description,
        )

        return self.columns, utils.get_item_properties(alias, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            "name",
            nargs='+',
            help="Function Alias name(s).",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        self.delete = client.function_aliases.delete
        self.resource = 'function_alias'

        self.delete_resources(parsed_args.name)


class Show(command.ShowOne):
    columns = base.FUNCTION_ALIAS_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)

        parser.add_argument(
            "name",
            help="Function Alias name.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        alias = client.function_aliases.get(parsed_args.name)

        return self.columns, utils.get_item_properties(alias, self.columns)


class Update(command.ShowOne):
    columns = base.FUNCTION_ALIAS_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            "name",
            help="Function Alias name.",
        )
        parser.add_argument(
            "--function",
            help="Function ID or Name.",
        )
        parser.add_argument(
            "--function-version",
            help="Function Version number.",
        )
        parser.add_argument(
            "--description",
            help="Description for the new alias.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        function_id = parsed_args.function
        if function_id and not uuidutils.is_uuid_like(function_id):
            # Try to find the function id with name
            function_id = q_utils.find_resource_id_by_name(
                client.functions, function_id)

        alias = client.function_aliases.update(
            parsed_args.name,
            function_id=function_id,
            function_version=parsed_args.function_version,
            description=parsed_args.description,
        )

        return self.columns, utils.get_item_properties(alias, self.columns)
