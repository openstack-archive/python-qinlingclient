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

import abc
import textwrap

from osc_lib.command import command
from osc_lib import utils
import six

from qinlingclient.common import exceptions
from qinlingclient.i18n import _

RUNTIME_COLUMNS = (
    'id',
    'name',
    'image',
    'status',
    'description',
    'is_public',
    'trusted',
    'project_id',
    'created_at',
    'updated_at'
)
RUNTIME_POOL_COLUMNS = (
    'name',
    'capacity'
)
FUNCTION_COLUMNS = (
    'id',
    'name',
    'description',
    'count',
    'code',
    'runtime_id',
    'entry',
    'project_id',
    'created_at',
    'updated_at',
    'cpu',
    'memory_size'
)
EXECUTION_COLUMNS = (
    'id',
    'function_id',
    'function_version',
    'description',
    'input',
    'result',
    'status',
    'sync',
    'project_id',
    'created_at',
    'updated_at'
)
JOB_COLUMNS = (
    'id',
    'name',
    'count',
    'status',
    'function_id',
    'function_version',
    'function_input',
    'pattern',
    'first_execution_time',
    'next_execution_time',
    'project_id',
    'created_at',
    'updated_at'
)
WORKER_COLUMNS = (
    'function_id',
    'worker_name'
)
WEBHOOK_COLUMNS = (
    'id',
    'function_id',
    'function_version',
    'description',
    'project_id',
    'created_at',
    'updated_at',
    'webhook_url'
)
FUNCTION_VERSION_COLUMNS = (
    'id',
    'function_id',
    'description',
    'version_number',
    'count',
    'project_id',
    'created_at',
    'updated_at'
)


@six.add_metaclass(abc.ABCMeta)
class QinlingLister(command.Lister):
    columns = ()

    def get_parser(self, prog_name):
        parser = super(QinlingLister, self).get_parser(prog_name)
        parser.add_argument(
            '--filter',
            dest='filters',
            action='append',
            help=_(
                'Filters for resource query that can be repeated. Supported '
                'operands: eq, neq, in, nin, gt, gte, lt, lte, has. '
                'E.g. --filter key="neq:123". The available keys are {0}'
            ).format(self.columns)
        )

        return parser

    @abc.abstractmethod
    def _get_resources(self, parsed_args):
        """Gets a list of API resources (e.g. using client)."""
        raise NotImplementedError

    def _validate_parsed_args(self, parsed_args):
        # No-op by default.
        pass

    def _headers(self):
        return [c.capitalize() for c in self.columns]

    def take_action(self, parsed_args):
        self._validate_parsed_args(parsed_args)

        ret = self._get_resources(parsed_args)
        if not isinstance(ret, list):
            ret = [ret]

        return (
            self._headers(),
            list(utils.get_item_properties(
                s,
                self.columns,
            ) for s in ret)
        )


class QinlingDeleter(command.Command):
    def delete_resources(self, ids):
        """Delete one or more resources."""
        failure_flag = False
        success_msg = "Request to delete %s %s has been accepted."
        error_msg = "Unable to delete the specified %s(s)."

        for id in ids:
            try:
                self.delete(id)
                print(success_msg % (self.resource, id))
            except Exception as e:
                failure_flag = True
                print(e)

        if failure_flag:
            raise exceptions.QinlingClientException(error_msg % self.resource)


def cut(string, length=25):
    if string and len(string) > length:
        return "%s..." % string[:length]
    else:
        return string


def wrap(string, width=25):
    if string and len(string) > width:
        return textwrap.fill(string, width)
    else:
        return string


def get_filters(parsed_args):
    filters = {}

    if hasattr(parsed_args, 'filters') and parsed_args.filters:
        for f in parsed_args.filters:
            arr = f.split('=')

            if len(arr) != 2:
                raise ValueError('Invalid filter: %s' % f)

            filters[arr[0]] = arr[1]

    return filters
