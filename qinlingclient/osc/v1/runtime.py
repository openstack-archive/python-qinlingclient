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

from qinlingclient.osc.v1 import base


class List(base.QinlingLister):
    columns = base.RUNTIME_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.runtimes.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.RUNTIME_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "image",
            metavar='IMAGE',
            help="Container image name used by runtime.",
        )
        parser.add_argument(
            "--name",
            help="Runtime name.",
        )
        parser.add_argument(
            "--description",
            help="Runtime description.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        runtime = client.runtimes.create(
            name=parsed_args.name,
            description=parsed_args.description,
            image=parsed_args.image
        )

        return self.columns, utils.get_item_properties(runtime, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'runtime',
            nargs='+',
            metavar='RUNTIME',
            help='Id of runtime(s).'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.runtimes.delete
        self.resource = 'runtime'

        self.delete_resources(parsed_args.runtime)


class Show(command.ShowOne):
    columns = base.RUNTIME_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('runtime', help='Runtime ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        runtime = client.runtimes.get(parsed_args.runtime)

        return self.columns, utils.get_item_properties(runtime, self.columns)


class Pool(command.ShowOne):
    columns = base.RUNTIME_POOL_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Pool, self).get_parser(prog_name)
        parser.add_argument('runtime', help='Runtime ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        pool = client.runtimes.get_pool(parsed_args.runtime)
        return self.columns, utils.get_item_properties(pool,
                                                       self.columns)
