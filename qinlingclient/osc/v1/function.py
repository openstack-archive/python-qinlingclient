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
import shutil
import tempfile
import zipfile

from osc_lib.command import command
from osc_lib import utils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient import utils as q_utils

MAX_ZIP_SIZE = 50 * 1024 * 1024


def _get_package_file(package_path=None, file_path=None):
    if package_path:
        if not zipfile.is_zipfile(package_path):
            raise exceptions.QinlingClientException(
                'Package %s is not a valid ZIP file.' % package_path
            )

        if os.path.getsize(package_path) > MAX_ZIP_SIZE:
            raise exceptions.QinlingClientException(
                'Package file size must be no more than %sM.' %
                (MAX_ZIP_SIZE / 1024 / 1024)
            )

        return package_path

    elif file_path:
        if not os.path.isfile(file_path):
            raise exceptions.QinlingClientException(
                'File %s not exist.' % file_path
            )

        base_name, extension = os.path.splitext(file_path)
        base_name = os.path.basename(base_name)
        zip_file = os.path.join(
            tempfile.gettempdir(),
            '%s.zip' % base_name
        )

        zf = zipfile.ZipFile(zip_file, mode='w')
        try:
            # Use default compression mode, may change in future.
            zf.write(
                file_path,
                '%s%s' % (base_name, extension),
                compress_type=zipfile.ZIP_STORED
            )
        finally:
            zf.close()

        if os.path.getsize(zip_file) > MAX_ZIP_SIZE:
            raise exceptions.QinlingClientException(
                'Package file size must be no more than %sM.' %
                (MAX_ZIP_SIZE / 1024 / 1024)
            )

        return zip_file


def worker_count(value):
    try:
        value = int(value)
        if value <= 0:
            raise ValueError
    except ValueError:
        raise exceptions.QinlingClientException(
            'Worker count must be a positive integer.'
        )
    return value


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
            required=False,
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

        if not parsed_args.code_type:
            if (parsed_args.file or parsed_args.package):
                parsed_args.code_type = 'package'
            elif (parsed_args.container or parsed_args.object):
                parsed_args.code_type = 'swift'
            elif parsed_args.image:
                parsed_args.code_type = 'image'

        if parsed_args.code_type == 'package':
            if not (parsed_args.file or parsed_args.package):
                raise exceptions.QinlingClientException(
                    'Package or file needs to be specified.'
                )
            if not parsed_args.runtime:
                raise exceptions.QinlingClientException(
                    'Runtime needs to be specified for package type function.'
                )

            zip_file = _get_package_file(parsed_args.package, parsed_args.file)
            md5sum = q_utils.md5(file=zip_file)
            code = {"source": "package", "md5sum": md5sum}

            with open(zip_file, 'rb') as package:
                function = client.functions.create(
                    name=parsed_args.name,
                    runtime=parsed_args.runtime,
                    code=code,
                    package=package,
                    entry=parsed_args.entry,
                )

            # Delete zip file the client created
            if parsed_args.file and not parsed_args.package:
                os.remove(zip_file)

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
        return self.columns, utils.get_item_properties(function,
                                                       self.columns)


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
            help="Function entry in the format of <module_name>.<method_name>"
        )

        package_group = parser.add_argument_group('package_group')
        swift_group = parser.add_argument_group('swift_group')

        group = package_group.add_mutually_exclusive_group()
        group.add_argument(
            "--file",
            metavar="CODE_FILE_PATH",
            help="Code file path."
        )
        group.add_argument(
            "--package",
            metavar="CODE_PACKAGE_PATH",
            help="Code package zip file path."
        )

        swift_group.add_argument(
            "--container",
            help="Container name in Swift.",
        )
        swift_group.add_argument(
            "--object",
            help="Object name in Swift.",
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        code = None
        package = None
        zip_file = None

        if parsed_args.file or parsed_args.package:
            code = {'source': 'package'}
            zip_file = _get_package_file(parsed_args.package, parsed_args.file)
        elif parsed_args.container or parsed_args.object:
            code = {
                'source': 'swift',
                'swift': {
                    'container': parsed_args.container,
                    'object': parsed_args.object
                }
            }

        if zip_file:
            with open(zip_file, 'rb') as package:
                func = client.functions.update(
                    parsed_args.id,
                    code=code,
                    package=package,
                    name=parsed_args.name,
                    description=parsed_args.description,
                    entry=parsed_args.entry,
                )
        else:
            func = client.functions.update(
                parsed_args.id,
                code=code,
                name=parsed_args.name,
                description=parsed_args.description,
                entry=parsed_args.entry,
            )

        return self.columns, utils.get_item_properties(func, self.columns)


class Detach(command.Command):
    def get_parser(self, prog_name):
        parser = super(Detach, self).get_parser(prog_name)
        parser.add_argument('function', help='Function ID.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        success_msg = "Request to detach function %s has been accepted."
        error_msg = "Unable to detach the specified function."

        try:
            client.functions.detach(parsed_args.function)
            print(success_msg % parsed_args.function)
        except Exception as e:
            print(e)
            raise exceptions.QinlingClientException(error_msg)


class Download(command.Command):
    def get_parser(self, prog_name):
        parser = super(Download, self).get_parser(prog_name)
        parser.add_argument('function', help='Function ID.')
        parser.add_argument(
            "-o",
            "--output",
            help="Target file path. If not provided, function ID will be used"
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        res = client.functions.get(parsed_args.function, download=True)

        cwd = os.getcwd()
        if parsed_args.output:
            if os.path.isabs(parsed_args.output):
                abs_path = parsed_args.output
            else:
                abs_path = os.path.join(cwd, parsed_args.output)
        else:
            abs_path = os.path.join(cwd, "%s.zip" % parsed_args.function)

        with open(abs_path, 'wb') as target:
            shutil.copyfileobj(res.raw, target)
        print("Code package downloaded to %s" % (abs_path))


class Scaleup(command.Command):
    def get_parser(self, prog_name):
        parser = super(Scaleup, self).get_parser(prog_name)
        parser.add_argument('function', help='Function ID.')
        parser.add_argument('--count', type=worker_count, default=1,
                            help='Number of workers to scale up.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        success_msg = "Request to scale up function %s has been accepted."
        error_msg = "Unable to scale up the specified function."

        try:
            client.functions.scaleup(parsed_args.function, parsed_args.count)
            print(success_msg % parsed_args.function)
        except Exception as e:
            print(e)
            raise exceptions.QinlingClientException(error_msg)


class Scaledown(command.Command):
    def get_parser(self, prog_name):
        parser = super(Scaledown, self).get_parser(prog_name)
        parser.add_argument('function', help='Function ID.')
        parser.add_argument('--count', type=worker_count, default=1,
                            help='Number of workers to scale down.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.function_engine
        success_msg = "Request to scale down function %s has been accepted."
        error_msg = "Unable to scale down the specified function."

        try:
            client.functions.scaledown(parsed_args.function, parsed_args.count)
            print(success_msg % parsed_args.function)
        except Exception as e:
            print(e)
            raise exceptions.QinlingClientException(error_msg)
