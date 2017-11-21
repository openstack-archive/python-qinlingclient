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
import os
import tempfile
import zipfile

from osc_lib.command import command
from osc_lib import utils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base


class List(base.QinlingLister):
    columns = base.FUNCTION_COLUMNS

    def _get_resources(self, parsed_args):
        client = self.app.client_manager.function_engine

        return client.functions.list(**base.get_filters(parsed_args))


class Create(command.ShowOne):
    columns = base.FUNCTION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Create, self).get_parser(prog_name)

        parser.add_argument(
            "--code-type",
            choices=['package', 'swift', 'image'],
            required=True,
            help="Code type.",
        )
        parser.add_argument(
            "--runtime",
            help="Runtime ID.",
        )
        parser.add_argument(
            "--name",
            help="Function name.",
        )
        parser.add_argument(
            "--entry",
            help="Function entry in the format of <module_name>.<method_name>"
        )
        protected_group = parser.add_mutually_exclusive_group(required=False)
        protected_group.add_argument(
            "--file",
            metavar="CODE_FILE_PATH",
            help="Code file path."
        )
        protected_group.add_argument(
            "--package",
            metavar="CODE_PACKAGE_PATH",
            help="Code package zip file path."
        )
        parser.add_argument(
            "--container",
            help="Container name in Swift.",
        )
        parser.add_argument(
            "--object",
            help="Object name in Swift.",
        )
        parser.add_argument(
            "--image",
            help="Image name in docker hub.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine

        if parsed_args.code_type == 'package':
            zip_file = None

            if not (parsed_args.file or parsed_args.package):
                raise exceptions.QinlingClientException(
                    'Package or file needs to be specified.'
                )
            if not parsed_args.runtime:
                raise exceptions.QinlingClientException(
                    'Runtime needs to be specified for package type function.'
                )

            if parsed_args.file:
                if not os.path.isfile(parsed_args.file):
                    raise exceptions.QinlingClientException(
                        'File %s not exist.' % parsed_args.file
                    )

                base_name, extention = os.path.splitext(parsed_args.file)
                base_name = os.path.basename(base_name)
                zip_file = os.path.join(
                    tempfile.gettempdir(),
                    '%s.zip' % base_name
                )

                zf = zipfile.ZipFile(zip_file, mode='w')
                try:
                    # Use default compression mode, may change in future.
                    zf.write(
                        parsed_args.file,
                        '%s%s' % (base_name, extention),
                        compress_type=zipfile.ZIP_STORED
                    )
                finally:
                    zf.close()
            if parsed_args.package:
                if not zipfile.is_zipfile(parsed_args.package):
                    raise exceptions.QinlingClientException(
                        'Package %s is not a valid ZIP file.' %
                        parsed_args.package
                    )
                zip_file = parsed_args.package

            with open(zip_file, 'rb') as package:
                function = client.functions.create(
                    name=parsed_args.name,
                    runtime=parsed_args.runtime,
                    code={"source": "package"},
                    package=package,
                    entry=parsed_args.entry,
                )
        elif parsed_args.code_type == 'swift':
            if not (parsed_args.container and parsed_args.object):
                raise exceptions.QinlingClientException(
                    'Container name and object name need to be specified.'
                )
            if not parsed_args.runtime:
                raise exceptions.QinlingClientException(
                    'Runtime needs to be specified for package type function.'
                )

            code = {
                "source": "swift",
                "swift": {
                    "container": parsed_args.container,
                    "object": parsed_args.object
                }
            }

            function = client.functions.create(
                name=parsed_args.name,
                runtime=parsed_args.runtime,
                code=code,
                entry=parsed_args.entry,
            )
        elif parsed_args.code_type == 'image':
            if not parsed_args.image:
                raise exceptions.QinlingClientException(
                    'Image needs to be specified.'
                )

            code = {
                "source": "image",
                "image": parsed_args.image
            }

            function = client.functions.create(
                name=parsed_args.name,
                code=code,
                entry=parsed_args.entry,
            )

        return self.columns, utils.get_item_properties(function, self.columns)


class Delete(base.QinlingDeleter):
    def get_parser(self, prog_name):
        parser = super(Delete, self).get_parser(prog_name)

        parser.add_argument(
            'function',
            nargs='+',
            metavar='FUNCTION',
            help='Id of function(s).'
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        self.delete = client.functions.delete
        self.resource = 'function'

        self.delete_resources(parsed_args.function)


class Show(command.ShowOne):
    columns = base.FUNCTION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Show, self).get_parser(prog_name)
        parser.add_argument('function', help='Function ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        function = client.functions.get(parsed_args.function)

        return self.columns, utils.get_item_properties(function, self.columns)


class Update(command.ShowOne):
    columns = base.FUNCTION_COLUMNS

    def get_parser(self, prog_name):
        parser = super(Update, self).get_parser(prog_name)

        parser.add_argument(
            'id',
            help='Function ID.'
        )
        parser.add_argument(
            "--name",
            help="Function name."
        )
        parser.add_argument(
            "--description",
            help="Function description."
        )
        parser.add_argument(
            "--entry",
            help="Function entry, in the format of <module_name>.<method_name>"
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        func = client.functions.update(
            parsed_args.id,
            name=parsed_args.name,
            description=parsed_args.description,
            entry=parsed_args.entry,
        )

        return self.columns, utils.get_item_properties(func, self.columns)
