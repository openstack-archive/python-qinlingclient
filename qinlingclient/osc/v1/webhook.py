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
    columns = base.WEBHOOK_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.webhooks.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.WEBHOOK_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )
        parser.add_argument(
            "--description",
            help="Webhook description.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        webhook = client.webhooks.create(
            function_id=parsed_args.function_id,
            description=parsed_args.description,
        )

        return self.columns, utils.get_item_properties(webhook, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'webhook',
            nargs='+',
            help='Id of webhook(s).'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.webhooks.delete
        self.resource = 'webhook'

        self.delete_resources(parsed_args.webhook)


class Show(command.ShowOne):
    columns = base.WEBHOOK_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('webhook', help='Webhook ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        webhook = client.webhooks.get(parsed_args.webhook)

        return self.columns, utils.get_item_properties(webhook, self.columns)


class Update(command.ShowOne):
    columns = base.WEBHOOK_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Webhook ID.'
        )
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--function-id",
            help="Function ID."
        )
        group.add_argument(
            "--description",
            help="Webhook description."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        webhook = client.webhooks.update(
            parsed_args.id,
            function_id=parsed_args.function_id,
            description=parsed_args.description
        )

        return self.columns, utils.get_item_properties(webhook, self.columns)
