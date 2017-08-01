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
from osc_lib import utils as osc_utils

from qinlingclient.osc.v1 import base


class List(base.QinlingLister):
    columns = base.JOB_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.jobs.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.JOB_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "function_id",
            help="Function ID.",
        )

        parser.add_argument(
            "--name",
            help="Job name."
        )
        parser.add_argument(
            "--first-execution-time",
            help="The earliest execution time(UTC) for the job."
        )
        parser.add_argument(
            "--pattern",
            help="The cron pattern for job execution."
        )
        parser.add_argument(
            "--function-input",
            help="Function input."
        )
        parser.add_argument(
            "--count",
            type=int,
            help="Expected number of executions triggered by job."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        job = client.jobs.create(
            function_id=parsed_args.function_id,
            name=parsed_args.name,
            first_execution_time=parsed_args.first_execution_time,
            pattern=parsed_args.pattern,
            function_input=parsed_args.function_input,
            count=parsed_args.count
        )

        return self.columns, osc_utils.get_item_properties(job, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'job',
            nargs='+',
            help='Job ID(s).'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.jobs.delete
        self.resource = 'job'

        self.delete_resources(parsed_args.job)


class Show(command.ShowOne):
    columns = base.JOB_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('job', help='Job ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        job = client.jobs.get(parsed_args.job)

        return self.columns, osc_utils.get_item_properties(job, self.columns)


class Update(command.ShowOne):
    columns = base.JOB_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Job ID.'
        )
        parser.add_argument(
            "--name",
            help="Job name."
        )
        parser.add_argument(
            "--status",
            choices=['running', 'paused', 'done', 'cancelled'],
            help="Job status."
        )
        parser.add_argument(
            "--next-execution-time",
            help="The next execution time(UTC) for the job."
        )
        parser.add_argument(
            "--pattern",
            help="The cron pattern for job execution."
        )
        parser.add_argument(
            "--function-input",
            help="Function input."
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        job = client.jobs.update(
            parsed_args.id,
            name=parsed_args.name,
            status=parsed_args.status,
            pattern=parsed_args.pattern,
            next_execution_time=parsed_args.next_execution_time,
            function_input=parsed_args.function_input,
        )

        return self.columns, osc_utils.get_item_properties(job, self.columns)
