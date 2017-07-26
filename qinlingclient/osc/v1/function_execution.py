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
from oslo_serialization import jsonutils

from qinlingclient.osc.v1 import base


class List(base.QinlingLister):
    columns = base.EXECUTION_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.function_executions.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.EXECUTION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "function",
            metavar='FUNCTION_ID',
            help="Function ID.",
        )
        parser.add_argument(
            "--input",
            metavar='INPUT',
            help="Input for the function.",
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--sync",
            action='store_true',
            help="Run execution synchronously."
        )
        group.add_argument(
            "--async",
            action='store_true',
            help="Run execution asynchronously.",
        )

        return parser

    def take_action(self, parsed_args):
        if parsed_args.input:
            input = jsonutils.loads(parsed_args.input)
        else:
            input = {}

        client = self.app.client_manager.function_engine
        execution = client.function_executions.create(
            function=parsed_args.function,
            sync=parsed_args.sync,
            input=input
        )

        return self.columns, utils.get_item_properties(execution, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'execution',
            nargs='+',
            metavar='EXECUTION',
            help='ID of function execution(s).'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.function_executions.delete
        self.resource = 'execution'

        self.delete_resources(parsed_args.execution)


class Show(command.ShowOne):
    columns = base.EXECUTION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('execution', help='Execution ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        execution = client.function_executions.get(parsed_args.execution)

        return self.columns, utils.get_item_properties(execution, self.columns)
