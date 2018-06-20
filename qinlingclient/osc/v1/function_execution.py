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

from qinlingclient.osc.v1 import base
from qinlingclient import utils as q_utils


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
            metavar='FUNCTION',
            help="Function name or ID.",
        )
        parser.add_argument(
            "--function-version",
            type=int,
            default=0,
            help="Function version number.",
        )
        parser.add_argument(
            "--input",
            help="Input for the function.",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--sync",
            action='store_true',
            dest='sync',
            default=True,
            help="Run execution synchronously."
        )
        group.add_argument(
            "--async",
            action='store_false',
            dest='sync',
            default=True,
            help="Run execution asynchronously.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        function = parsed_args.function
        if not uuidutils.is_uuid_like(function):
            # Try to find the function id with name
            function = q_utils.find_resource_id_by_name(
                client.functions, function)

        execution = client.function_executions.create(
            function=function,
            version=parsed_args.function_version,
            sync=parsed_args.sync,
            input=parsed_args.input
        )

        return self.columns, utils.get_item_properties(execution, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--execution",
            nargs='+',
            help="ID of function execution(s)."
        )
        group.add_argument(
            "--function",
            nargs='+',
            help="ID of function(s)."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.function_executions.delete
        self.resource = 'execution'

        if parsed_args.execution:
            self.delete_resources(parsed_args.execution)
        elif parsed_args.function:
            for f in parsed_args.function:
                execs = client.function_executions.list(function_id=f)
                ids = [e.id for e in execs]
                self.delete_resources(ids)


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


class LogShow(command.Command):
    def get_parser(self, prog_name):
        parser = super(LogShow, self).get_parser(prog_name)
        parser.add_argument('execution', help='Execution ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        log = client.function_executions.get_log(parsed_args.execution)

        self.app.stdout.write(log or "\n")
