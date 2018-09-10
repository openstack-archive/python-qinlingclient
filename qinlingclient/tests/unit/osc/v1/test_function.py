# Copyright 2018 AWCloud Software Co., Ltd.
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

import mock
import zipfile

from osc_lib.tests import utils as osc_tests_utils
import testtools

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient.osc.v1 import function
from qinlingclient.tests.unit.osc.v1 import fakes


class TestFunctionUtils(testtools.TestCase):

    def setUp(self):
        super(TestFunctionUtils, self).setUp()

    @mock.patch('zipfile.is_zipfile')
    @mock.patch('os.path.getsize')
    def test__get_package_file_package(self, getsize_mock, is_zipfile_mock):
        is_zipfile_mock.return_value = True
        getsize_mock.return_value = function.MAX_ZIP_SIZE

        package_path = '/PATH/TO/FAKE_PACKAGE.ZIP'

        ret = function._get_package_file(package_path=package_path)

        self.assertEqual(package_path, ret)

        is_zipfile_mock.assert_called_once_with(package_path)
        getsize_mock.assert_called_once_with(package_path)

    @mock.patch('zipfile.is_zipfile')
    def test__get_package_file_package_not_a_valid_zip_file(self,
                                                            is_zipfile_mock):
        is_zipfile_mock.return_value = False

        package_path = '/PATH/TO/NOT_A_ZIP_FILE.py'

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            "^Package %s is not a valid ZIP file\.$" % package_path,
            function._get_package_file, package_path=package_path)

        is_zipfile_mock.assert_called_once_with(package_path)

    @mock.patch('zipfile.is_zipfile')
    @mock.patch('os.path.getsize')
    def test__get_package_file_package_size_exceed(self, getsize_mock,
                                                   is_zipfile_mock):
        is_zipfile_mock.return_value = True
        getsize_mock.return_value = function.MAX_ZIP_SIZE + 1

        package_path = '/PATH/TO/FAKE_PACKAGE.ZIP'

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Package file size must be no more than %sM\.$' % (
                function.MAX_ZIP_SIZE / 1024 / 1024),
            function._get_package_file, package_path=package_path)

        is_zipfile_mock.assert_called_once_with(package_path)
        getsize_mock.assert_called_once_with(package_path)

    @mock.patch('os.path.isfile')
    @mock.patch('tempfile.gettempdir')
    @mock.patch('zipfile.ZipFile')
    @mock.patch('os.path.getsize')
    def test__get_package_file_file(self, getsize_mock, ZipFileClassMock,
                                    gettempdir_mock, isfile_mock):
        isfile_mock.return_value = True
        fake_tempdir_path = '/FAKE/TEMP_DIR'
        gettempdir_mock.return_value = fake_tempdir_path
        fake_zf = mock.Mock()
        ZipFileClassMock.return_value = fake_zf
        getsize_mock.return_value = function.MAX_ZIP_SIZE

        base_name = 'FAKE_FILE'
        extension = '.py'
        file_path = '/PATH/TO/%s%s' % (base_name, extension)
        zip_file_path = '%s/%s.zip' % (fake_tempdir_path, base_name)

        ret = function._get_package_file(file_path=file_path)

        self.assertEqual(zip_file_path, ret)

        isfile_mock.assert_called_once_with(file_path)
        ZipFileClassMock.assert_called_once_with(zip_file_path, mode='w')
        fake_zf.write.assert_called_once_with(
            file_path, '%s%s' % (base_name, extension),
            compress_type=zipfile.ZIP_STORED)
        fake_zf.close.assert_called_once_with()
        getsize_mock.assert_called_once_with(zip_file_path)

    @mock.patch('os.path.isfile')
    def test__get_package_file_file_not_exist(self, isfile_mock):
        isfile_mock.return_value = False

        file_path = '/PATH/TO/A_NON_EXIST_FILE.py'

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            "^File %s not exist\.$" % file_path,
            function._get_package_file, file_path=file_path)

        isfile_mock.assert_called_once_with(file_path)

    @mock.patch('os.path.isfile')
    @mock.patch('tempfile.gettempdir')
    @mock.patch('zipfile.ZipFile')
    @mock.patch('os.path.getsize')
    def test__get_package_file_file_zipped_size_exceed(self, getsize_mock,
                                                       ZipFileClassMock,
                                                       gettempdir_mock,
                                                       isfile_mock):
        isfile_mock.return_value = True
        fake_tempdir_path = '/FAKE/TEMP_DIR'
        gettempdir_mock.return_value = fake_tempdir_path
        fake_zf = mock.Mock()
        ZipFileClassMock.return_value = fake_zf
        getsize_mock.return_value = function.MAX_ZIP_SIZE + 1

        base_name = 'FAKE_FILE'
        extension = '.py'
        file_path = '/PATH/TO/%s%s' % (base_name, extension)
        zip_file_path = '%s/%s.zip' % (fake_tempdir_path, base_name)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Package file size must be no more than %sM\.$' % (
                function.MAX_ZIP_SIZE / 1024 / 1024),
            function._get_package_file, file_path=file_path)

        isfile_mock.assert_called_once_with(file_path)
        ZipFileClassMock.assert_called_once_with(zip_file_path, mode='w')
        fake_zf.write.assert_called_once_with(
            file_path, '%s%s' % (base_name, extension),
            compress_type=zipfile.ZIP_STORED)
        fake_zf.close.assert_called_once_with()
        getsize_mock.assert_called_once_with(zip_file_path)


class TestFunction(fakes.TestQinlingClient):

    def setUp(self):
        super(TestFunction, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.FUNCTION_COLUMNS
        self.data = []

        self._runtimes = fakes.FakeRuntime.create_runtimes(count=2)
        self._functions = fakes.FakeFunction.create_functions(count=3)
        for f in self._functions:
            self.data.append((f.id, f.name, f.description, f.count, f.code,
                              f.runtime_id, f.entry, f.project_id,
                              f.created_at, f.updated_at,
                              f.cpu, f.memory_size, f.timeout))


class TestListFunction(TestFunction):

    def setUp(self):
        super(TestListFunction, self).setUp()
        self.cmd = function.List(self.app, None)

        self.columns = [c.capitalize() for c in base.FUNCTION_COLUMNS]

        self.client.functions.list = mock.Mock(return_value=self._functions)

    def test_function_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.functions.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_list_with_filter(self):
        arglist = ['--filter', 'name=has:function',
                   '--filter', 'cpu=lt:200']
        verifylist = [
            ('filters', ['name=has:function', 'cpu=lt:200'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.functions.list.assert_called_once_with(
            name='has:function', cpu='lt:200'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_list_with_invalid_filter(self):
        arglist = ['--filter', 'name']
        verifylist = [
            ('filters', ['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            ValueError,
            '^Invalid filter: name$',
            self.cmd.take_action, parsed_args
        )


class TestCreateFunction(TestFunction):

    def setUp(self):
        super(TestCreateFunction, self).setUp()
        self.cmd = function.Create(self.app, None)
        self.runtime_id = self._runtimes[0].id
        self.runtime_name = self._runtimes[0].name
        self.function_name = 'FAKE_FUNCTION_NAME'
        self.function_entry = 'fake_module.fake_method'
        self.file_path = '/PATH/TO/functon.py'
        self.package_path = '/FAKE_TEMP_DIR/ZIPPED_function.zip'
        self.container_name = 'FAKE_SWIFT_CONTAINER'
        self.object_name = 'FAKE_SWIFT_OBJECT'
        self.image = 'FAKE_IMAGE'
        self.cpu = 200
        self.memory_size = 64 * 1024 * 1024
        self.timeout = 10
        # The arguments below are used in every create call despite of the
        # function type.
        self.base_call_arguments_default_values = {
            'name': None,
            'entry': None,
            'cpu': None,
            'memory_size': None,
            'timeout': 5
        }
        self.base_call_arguments_passed_values = {
            'name': self.function_name,
            'entry': self.function_entry,
            'cpu': self.cpu,
            'memory_size': self.memory_size,
            'timeout': self.timeout
        }

    def _create_fake_function(self, attrs=None):
        # Allow to fake different create results
        f = fakes.FakeFunction.create_one_function(attrs)
        self.client.functions.create = mock.Mock(return_value=f)
        data = (f.id, f.name, f.description, f.count, f.code,
                f.runtime_id, f.entry, f.project_id,
                f.created_at, f.updated_at,
                f.cpu, f.memory_size, f.timeout)
        return data

    def _get_verify_list(self, runtime=None, name=None, entry=None,
                         file_path=None, package_path=None,
                         container_name=None, object_name=None,
                         image=None, cpu=None, memory_size=None, timeout=5):
        return [
            ('runtime', runtime),
            ('name', name),
            ('entry', entry),
            ('file', file_path),
            ('package', package_path),
            ('container', container_name),
            ('object', object_name),
            ('image', image),
            ('cpu', cpu),
            ('memory_size', memory_size),
            ('timeout', timeout)
        ]

    def _get_verify_list_with_passed_value(self, **kwargs):
        kwargs.update({'name': self.function_name,
                       'entry': self.function_entry,
                       'cpu': self.cpu,
                       'memory_size': self.memory_size,
                       'timeout': self.timeout})
        return self._get_verify_list(**kwargs)

    def test_function_create_no_option(self):
        arglist = []
        verifylist = self._get_verify_list()

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Cannot create function with the parameters given.+',
            self.cmd.take_action, parsed_args)

    def test_function_create_file_and_package_mutually_exclusive(self):
        # --file and --package are mutually exclusive
        arglist = ['--file', self.file_path, '--package', self.package_path]
        verifylist = self._get_verify_list(file_path=self.file_path,
                                           package_path=self.package_path)

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    @mock.patch('qinlingclient.osc.v1.function._get_package_file')
    @mock.patch('qinlingclient.utils.md5')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('os.remove')
    def test_function_create_package_required_options(
            self, remove_mock, open_mock, md5_mock, _get_package_file_mock):
        """Create a package type function.

        1. file param is specified,
        2. use runtime id,
        3. all other params except the required ones are not set.
        """
        md5sum = 'FAKE_MD5_SUM'
        code = {'source': 'package', 'md5sum': md5sum}
        attrs = {'runtime_id': self.runtime_id, 'code': code}
        created_data = self._create_fake_function(attrs)

        _get_package_file_mock.return_value = self.package_path
        md5_mock.return_value = md5sum
        package_file = mock.Mock()
        open_mock.return_value.__enter__.return_value = package_file

        arglist = ['--runtime', self.runtime_id, '--file', self.file_path]
        verifylist = self._get_verify_list(runtime=self.runtime_id,
                                           file_path=self.file_path)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'runtime': self.runtime_id,
                          'code': code,
                          'package': package_file}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        _get_package_file_mock.assert_called_once_with(None, self.file_path)
        md5_mock.assert_called_once_with(file=self.package_path)
        open_mock.assert_called_once_with(self.package_path, 'rb')
        remove_mock.assert_called_once_with(self.package_path)

    @mock.patch('qinlingclient.osc.v1.function._get_package_file')
    @mock.patch('qinlingclient.utils.md5')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('os.remove')
    def test_function_create_package_all_options(
            self, remove_mock, open_mock, md5_mock, _get_package_file_mock):
        """Create a package type function.

        1. package param is specified
        2. use runtime name,
        3. if acceptable, all options are specified with some value, so this
           also tests that package type is taking precedence of other types.
        """
        md5sum = 'FAKE_MD5_SUM'
        code = {'source': 'package', 'md5sum': md5sum}
        attrs = {
            'name': self.function_name,
            'code': code,
            'runtime_id': self.runtime_id,
            'entry': self.function_entry,
            'cpu': self.cpu,
            'memory_size': self.memory_size,
            'timeout': self.timeout
        }
        created_data = self._create_fake_function(attrs)

        _get_package_file_mock.return_value = self.package_path
        md5_mock.return_value = md5sum
        package_file = mock.Mock()
        open_mock.return_value.__enter__.return_value = package_file
        # Use to find the runtime id with its name
        self.client.runtimes.find.return_value = self._runtimes[0]

        arglist = [
            '--runtime', self.runtime_name,
            '--name', self.function_name,
            '--entry', self.function_entry,
            '--package', self.package_path,
            '--container', self.container_name,
            '--object', self.object_name,
            '--image', self.image,
            '--cpu', str(self.cpu),
            '--memory-size', str(self.memory_size),
            '--timeout', str(self.timeout)
        ]
        verifylist = self._get_verify_list_with_passed_value(
            runtime=self.runtime_name,
            package_path=self.package_path,
            container_name=self.container_name,
            object_name=self.object_name,
            image=self.image,
            cpu=self.cpu,
            memory_size=self.memory_size,
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'runtime': self.runtime_id,
                          'code': code,
                          'package': package_file}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.runtimes.find.assert_called_once_with(
            name=self.runtime_name)
        _get_package_file_mock.assert_called_once_with(self.package_path, None)
        md5_mock.assert_called_once_with(file=self.package_path)
        open_mock.assert_called_once_with(self.package_path, 'rb')

    def test_function_create_package_runtime_needed(self):
        """Create a package type function without runtime specified."""

        arglist = ['--file', self.file_path]
        verifylist = self._get_verify_list(file_path=self.file_path)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Runtime needs to be specified for package type function\.$',
            self.cmd.take_action, parsed_args)

    def test_function_create_swift_required_options(self):
        """Create a swift type function.

        1. use runtime id,
        2. all other params except the required ones are not set.
        """
        code = {
            'source': 'swift',
            'swift': {
                'container': self.container_name,
                'object': self.object_name
            }
        }
        attrs = {'runtime_id': self.runtime_id, 'code': code}
        created_data = self._create_fake_function(attrs)

        arglist = ['--runtime', self.runtime_id,
                   '--container', self.container_name,
                   '--object', self.object_name]
        verifylist = self._get_verify_list(runtime=self.runtime_id,
                                           container_name=self.container_name,
                                           object_name=self.object_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'runtime': self.runtime_id, 'code': code}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_create_swift_all_options(self):
        """Create a swift type function.

        1. use runtime name,
        2. if acceptable, all options are specified with some value, so this
           also tests that swift type is taking precedence of image type.
        """

        code = {
            'source': 'swift',
            'swift': {
                'container': self.container_name,
                'object': self.object_name
            }
        }
        attrs = {
            'name': self.function_name,
            'code': code,
            'runtime_id': self.runtime_id,
            'entry': self.function_entry,
            'cpu': self.cpu,
            'memory_size': self.memory_size,
            'timeout': self.timeout
        }
        created_data = self._create_fake_function(attrs)

        # Use to find the runtime id with its name
        self.client.runtimes.find.return_value = self._runtimes[0]

        arglist = [
            '--runtime', self.runtime_name,
            '--name', self.function_name,
            '--entry', self.function_entry,
            '--container', self.container_name,
            '--object', self.object_name,
            '--image', self.image,
            '--cpu', str(self.cpu),
            '--memory-size', str(self.memory_size),
            '--timeout', str(self.timeout)
        ]
        verifylist = self._get_verify_list_with_passed_value(
            runtime=self.runtime_name,
            container_name=self.container_name,
            object_name=self.object_name,
            image=self.image
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'runtime': self.runtime_id, 'code': code}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.runtimes.find.assert_called_once_with(
            name=self.runtime_name)

    def test_function_create_swift_container_needed(self):
        """Create a swift type function with only object given."""

        arglist = ['--object', self.object_name]
        verifylist = self._get_verify_list(object_name=self.object_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Container name and object name need to be specified\.$',
            self.cmd.take_action, parsed_args)

    def test_function_create_swift_object_needed(self):
        """Create a swift type function with only container given."""

        arglist = ['--container', self.container_name]
        verifylist = self._get_verify_list(container_name=self.container_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Container name and object name need to be specified\.$',
            self.cmd.take_action, parsed_args)

    def test_function_create_swift_runtime_needed(self):
        """Create a swift type function without runtime given."""

        arglist = ['--container', self.container_name,
                   '--object', self.object_name]
        verifylist = self._get_verify_list(container_name=self.container_name,
                                           object_name=self.object_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Runtime needs to be specified for swift type function\.$',
            self.cmd.take_action, parsed_args)

    def test_function_create_image_required_options(self):
        """Create a image type function with only required options."""

        code = {
            'source': 'image',
            'image': self.image
        }
        attrs = {'code': code}
        created_data = self._create_fake_function(attrs)

        arglist = ['--image', self.image]
        verifylist = self._get_verify_list(image=self.image)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': code}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_create_image_all_options(self):
        code = {
            'source': 'image',
            'image': self.image
        }
        attrs = {
            'name': self.function_name,
            'code': code,
            'entry': self.function_entry,
            'cpu': self.cpu,
            'memory_size': self.memory_size,
            'timeout': self.timeout
        }
        created_data = self._create_fake_function(attrs)

        arglist = [
            '--name', self.function_name,
            '--entry', self.function_entry,
            '--image', self.image,
            '--cpu', str(self.cpu),
            '--memory-size', str(self.memory_size),
            '--timeout', str(self.timeout)
        ]
        verifylist = self._get_verify_list_with_passed_value(image=self.image)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': code}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.create.assert_called_once_with(**call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_create_timeout_invalid(self):
        arglist = ['--timeout', '-1']
        verifylist = self._get_verify_list(timeout=-1)

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDeleteFunction(TestFunction):

    def setUp(self):
        super(TestDeleteFunction, self).setUp()
        self.cmd = function.Delete(self.app, None)
        self.client.functions.delete = mock.Mock(return_value=None)

    def test_function_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_delete_one(self):
        function_id = self._functions[0].id
        arglist = [function_id]
        verifylist = [('function', [function_id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.delete.assert_called_once_with(function_id)

    @mock.patch('qinlingclient.utils.find_resource_id_by_name')
    def test_function_delete_one_by_name(self, mock_find):
        name = self._functions[0].name
        id = self._functions[0].id
        mock_find.return_value = id
        arglist = [name]
        verifylist = [('function', [name])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.delete.assert_called_once_with(id)

    def test_function_delete_multiple(self):
        function_ids = [r.id for r in self._functions]
        arglist = function_ids
        verifylist = [('function', function_ids)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(f_id) for f_id in function_ids]
        self.assertEqual(len(function_ids),
                         self.client.functions.delete.call_count)
        self.client.functions.delete.assert_has_calls(calls)

    @mock.patch('qinlingclient.utils.find_resource_id_by_name')
    def test_function_delete_multiple_with_names(self, mock_find):
        function_ids = [r.id for r in self._functions[:-1]]
        function_names = [self._functions[-1].name]
        mock_find.return_value = self._functions[-1].id
        arglist = function_ids + function_names
        verifylist = [('function', function_ids + function_names)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

        expected = [mock.call(f_id) for f_id in function_ids]
        expected.append(mock.call(self._functions[-1].id))

        self.client.functions.delete.assert_has_calls(expected)

    def test_function_delete_multiple_exception(self):
        function_ids = [r.id for r in self._functions]
        arglist = function_ids
        verifylist = [('function', function_ids)]

        self.client.functions.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to delete the specified function\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deletion failed, but the third is done normally
        calls = [mock.call(f_id) for f_id in function_ids]
        self.assertEqual(len(function_ids),
                         self.client.functions.delete.call_count)
        self.client.functions.delete.assert_has_calls(calls)


class TestShowFunction(TestFunction):

    def setUp(self):
        super(TestShowFunction, self).setUp()
        self.cmd = function.Show(self.app, None)
        self.client.functions.get = mock.Mock(return_value=self._functions[0])

    def test_function_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_show(self):
        function_id = self._functions[0].id
        arglist = [function_id]
        verifylist = [('function', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.functions.get.assert_called_once_with(function_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)

    @mock.patch("qinlingclient.utils.find_resource_id_by_name")
    def test_function_show_by_name(self, mock_find):
        name = self._functions[0].name
        id = self._functions[0].id
        mock_find.return_value = id
        arglist = [name]
        verifylist = [('function', name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        mock_find.assert_called_once_with(self.client.functions, name)
        self.client.functions.get.assert_called_once_with(id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestUpdateFunction(TestFunction):

    def setUp(self):
        super(TestUpdateFunction, self).setUp()
        self.cmd = function.Update(self.app, None)
        self.function_id = self._functions[0].id
        self.function_name = 'FAKE_FUNCTION_NAME'
        self.function_description = 'This is a updated function.'
        self.function_entry = 'fake_module.fake_method'
        self.file_path = '/PATH/TO/functon.py'
        self.package_path = '/FAKE_TEMP_DIR/ZIPPED_function.zip'
        self.container_name = 'FAKE_SWIFT_CONTAINER'
        self.object_name = 'FAKE_SWIFT_OBJECT'
        self.image = 'FAKE_IMAGE'
        self.cpu = 200
        self.memory_size = 64 * 1024 * 1024
        self.timeout = 10
        # The arguments below are used in every update despite of the
        # function type.
        self.base_call_arguments_default_values = {
            'name': None,
            'description': None,
            'entry': None,
            'cpu': None,
            'memory_size': None,
            'timeout': None,
        }
        self.base_call_arguments_passed_values = {
            'name': self.function_name,
            'description': self.function_description,
            'entry': self.function_entry,
            'cpu': self.cpu,
            'memory_size': self.memory_size,
            'timeout': self.timeout
        }

    def _update_fake_function(self, attrs=None):
        # Allow to fake different update results
        f = fakes.FakeFunction.create_one_function(attrs)
        self.client.functions.update = mock.Mock(return_value=f)
        data = (f.id, f.name, f.description, f.count, f.code,
                f.runtime_id, f.entry, f.project_id,
                f.created_at, f.updated_at,
                f.cpu, f.memory_size, f.timeout)
        return data

    def _get_verify_list(self, function_id=None, name=None, description=None,
                         entry=None, file_path=None, package_path=None,
                         container_name=None, object_name=None,
                         cpu=None, memory_size=None, timeout=None):
        return [
            ('function', function_id),
            ('name', name),
            ('description', description),
            ('entry', entry),
            ('file', file_path),
            ('package', package_path),
            ('container', container_name),
            ('object', object_name),
            ('cpu', cpu),
            ('memory_size', memory_size),
            ('timeout', timeout)
        ]

    def _get_verify_list_with_passed_value(self, **kwargs):
        kwargs.update({'name': self.function_name,
                       'description': self.function_description,
                       'entry': self.function_entry,
                       'cpu': self.cpu,
                       'memory_size': self.memory_size,
                       'timeout': self.timeout})
        return self._get_verify_list(**kwargs)

    def test_function_update_no_option(self):
        arglist = []
        verifylist = self._get_verify_list()

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_update_required_options(self):
        """Update a function.

        Do nothing as only the function_id is specified.
        """
        attrs = {'id': self.function_id}
        updated_data = self._update_fake_function(attrs)

        arglist = [self.function_id]
        verifylist = self._get_verify_list(function_id=self.function_id)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': None}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    @mock.patch('qinlingclient.utils.find_resource_id_by_name')
    def test_function_update_by_name(self, mock_find):
        attrs = {'name': self.function_name, 'timeout': self.timeout}
        updated_data = self._update_fake_function(attrs)
        mock_find.return_value = self.function_id

        arglist = [self.function_name, '--timeout', str(self.timeout)]
        verifylist = self._get_verify_list(function_id=self.function_name,
                                           timeout=self.timeout)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        mock_find.assert_called_once_with(self.client.functions,
                                          self.function_name)

        call_arguments = {'code': None}
        call_arguments.update(self.base_call_arguments_default_values)
        call_arguments.update({'timeout': self.timeout})
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)

        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_function_update_code_not_updated(self):
        # All other options except code are updated.
        attrs = {'id': self.function_id,
                 'name': self.function_name,
                 'description': self.function_description,
                 'entry': self.function_entry,
                 'cpu': self.cpu,
                 'memory_size': self.memory_size,
                 'timeout': self.timeout}
        updated_data = self._update_fake_function(attrs)

        arglist = [
            self.function_id,
            '--name', self.function_name,
            '--description', self.function_description,
            '--entry', self.function_entry,
            '--cpu', str(self.cpu),
            '--memory-size', str(self.memory_size),
            '--timeout', str(self.timeout)
        ]
        verifylist = self._get_verify_list_with_passed_value(
            function_id=self.function_id)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': None}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_function_update_file_and_package_mutually_exclusive(self):
        # --file and --package are mutually exclusive
        arglist = [self.function_id,
                   '--file', self.file_path, '--package', self.package_path]
        verifylist = self._get_verify_list(function_id=self.function_id,
                                           file_path=self.file_path,
                                           package_path=self.package_path)

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    @mock.patch('qinlingclient.osc.v1.function._get_package_file')
    @mock.patch('qinlingclient.osc.v1.function.open')
    def test_function_update_package_required_options(
            self, open_mock, _get_package_file_mock):
        """Update a package type function.

        1. use --file to update the code,
        2. only required options are specified.
        """
        code = {'source': 'package'}
        attrs = {'id': self.function_id, 'code': code}
        updated_data = self._update_fake_function(attrs)

        _get_package_file_mock.return_value = self.package_path
        package_file = mock.Mock()
        open_mock.return_value.__enter__.return_value = package_file

        arglist = [self.function_id, '--file', self.file_path]
        verifylist = self._get_verify_list(function_id=self.function_id,
                                           file_path=self.file_path)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': code, 'package': package_file}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

        _get_package_file_mock.assert_called_once_with(None, self.file_path)
        open_mock.assert_called_once_with(self.package_path, 'rb')

    @mock.patch('qinlingclient.osc.v1.function._get_package_file')
    @mock.patch('qinlingclient.osc.v1.function.open')
    def test_function_update_package_all_options(
            self, open_mock, _get_package_file_mock):
        """Update a package type function.

        1. use --package to update the code,
        2. all the options are specified if acceptable, this also tests
           that package type is taking precedence of the swift type.
        """
        code = {'source': 'package'}
        attrs = {'id': self.function_id, 'code': code}
        updated_data = self._update_fake_function(attrs)

        _get_package_file_mock.return_value = self.package_path
        package_file = mock.Mock()
        open_mock.return_value.__enter__.return_value = package_file

        arglist = [self.function_id, '--package', self.package_path,
                   '--name', self.function_name,
                   '--description', self.function_description,
                   '--entry', self.function_entry,
                   '--container', self.container_name,
                   '--object', self.object_name,
                   '--cpu', str(self.cpu),
                   '--memory-size', str(self.memory_size),
                   '--timeout', str(self.timeout)]
        verifylist = self._get_verify_list_with_passed_value(
            function_id=self.function_id,
            package_path=self.package_path,
            container_name=self.container_name,
            object_name=self.object_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': code, 'package': package_file}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

        _get_package_file_mock.assert_called_once_with(self.package_path, None)
        open_mock.assert_called_once_with(self.package_path, 'rb')

    def test_function_update_swift_required_options(self):
        """Update a swift type function.

        1. only use --container to update the code.
        """
        code = {
            'source': 'swift',
            'swift': {
                'container': self.container_name,
                'object': "origin_obj"
            }
        }
        attrs = {'id': self.function_id, 'code': code}
        updated_data = self._update_fake_function(attrs)

        arglist = [self.function_id, '--container', self.container_name]
        verifylist = self._get_verify_list(function_id=self.function_id,
                                           container_name=self.container_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        code = {
            'source': 'swift',
            'swift': {
                'container': self.container_name,
            }
        }
        call_arguments = {'code': code}
        call_arguments.update(self.base_call_arguments_default_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_function_update_swift_all_options(self):
        """Update a swift type function.

        1. only both --container and --object to update the code,
        2. all other options are specified if appropriate.
        """
        code = {
            'source': 'swift',
            'swift': {
                'container': self.container_name,
                'object': self.object_name
            }
        }
        attrs = {'id': self.function_id, 'code': code}
        updated_data = self._update_fake_function(attrs)

        arglist = [self.function_id,
                   '--container', self.container_name,
                   '--object', self.object_name,
                   '--name', self.function_name,
                   '--description', self.function_description,
                   '--entry', self.function_entry,
                   '--cpu', str(self.cpu),
                   '--memory-size', str(self.memory_size),
                   '--timeout', str(self.timeout)]
        verifylist = self._get_verify_list_with_passed_value(
            function_id=self.function_id,
            container_name=self.container_name,
            object_name=self.object_name)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        call_arguments = {'code': code}
        call_arguments.update(self.base_call_arguments_passed_values)
        self.client.functions.update.assert_called_once_with(
            self.function_id, **call_arguments)
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_function_update_timeout_invalid(self):
        arglist = [self.function_id, '--timeout', '-1']
        verifylist = self._get_verify_list(function_id=self.function_id,
                                           timeout=-1)

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDetachFunction(TestFunction):

    def setUp(self):
        super(TestDetachFunction, self).setUp()
        self.cmd = function.Detach(self.app, None)
        self.client.functions.detach = mock.Mock(return_value=None)

    def test_function_detach_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_detach(self):
        function_id = self._functions[0].id
        arglist = [function_id]
        verifylist = [('function', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.detach.assert_called_once_with(function_id)

    def test_function_detach_exception(self):
        function_id = self._functions[0].id
        self.client.functions.detach = mock.Mock(side_effect=RuntimeError)

        arglist = [function_id]
        verifylist = [('function', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to detach the specified function\.$',
            self.cmd.take_action, parsed_args)

        self.client.functions.detach.assert_called_once_with(function_id)


class TestDownloadFunction(TestFunction):

    def setUp(self):
        super(TestDownloadFunction, self).setUp()
        self.cmd = function.Download(self.app, None)
        self.raw_data = 'RAW_DATA'
        self.cwd = '/FAKE/CWD'
        res = mock.Mock(raw=self.raw_data)
        self.client.functions.get = mock.Mock(return_value=res)

    def test_function_download_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    @mock.patch('os.getcwd')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('shutil.copyfileobj')
    def test_function_download_required_options(self, copyfile_mock, open_mock,
                                                getcwd_mock):
        function_id = self._functions[0].id

        getcwd_mock.return_value = self.cwd
        target = mock.Mock()
        open_mock.return_value.__enter__.return_value = target

        arglist = [function_id]
        verifylist = [('function', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.get.assert_called_once_with(function_id,
                                                          download=True)
        open_mock.assert_called_once_with(
            '%s/%s.zip' % (self.cwd, function_id), 'wb')
        copyfile_mock.assert_called_once_with(self.raw_data, target)

    @mock.patch('os.getcwd')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('shutil.copyfileobj')
    @mock.patch('qinlingclient.utils.find_resource_id_by_name')
    def test_function_download_by_name(self, find_mock, copyfile_mock,
                                       open_mock, getcwd_mock):
        name = self._functions[0].name
        id = self._functions[0].id
        find_mock.return_value = id
        getcwd_mock.return_value = self.cwd
        target = mock.Mock()
        open_mock.return_value.__enter__.return_value = target

        arglist = [name]
        verifylist = [('function', name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        find_mock.assert_called_once_with(self.client.functions, name)
        self.client.functions.get.assert_called_once_with(id,
                                                          download=True)
        open_mock.assert_called_once_with(
            '%s/%s.zip' % (self.cwd, id), 'wb')
        copyfile_mock.assert_called_once_with(self.raw_data, target)

    @mock.patch('os.getcwd')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('shutil.copyfileobj')
    def test_function_download_all_options(self, copyfile_mock, open_mock,
                                           getcwd_mock):
        function_id = self._functions[0].id
        output_name = 'output.zip'

        getcwd_mock.return_value = self.cwd
        target = mock.Mock()
        open_mock.return_value.__enter__.return_value = target

        arglist = [function_id, '--output', output_name]
        verifylist = [('function', function_id), ('output', output_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.get.assert_called_once_with(function_id,
                                                          download=True)
        open_mock.assert_called_once_with(
            '%s/%s' % (self.cwd, output_name), 'wb')
        copyfile_mock.assert_called_once_with(self.raw_data, target)

    @mock.patch('os.getcwd')
    @mock.patch('qinlingclient.osc.v1.function.open')
    @mock.patch('shutil.copyfileobj')
    def test_function_download_abs_path(self, copyfile_mock, open_mock,
                                        getcwd_mock):
        function_id = self._functions[0].id
        output_name = '/ABS_PATH/output.zip'

        getcwd_mock.return_value = self.cwd
        target = mock.Mock()
        open_mock.return_value.__enter__.return_value = target

        arglist = [function_id, '-o', output_name]
        verifylist = [('function', function_id), ('output', output_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.get.assert_called_once_with(function_id,
                                                          download=True)
        open_mock.assert_called_once_with(output_name, 'wb')
        copyfile_mock.assert_called_once_with(self.raw_data, target)


class TestScaleupFunction(TestFunction):

    def setUp(self):
        super(TestScaleupFunction, self).setUp()
        self.cmd = function.Scaleup(self.app, None)
        self.client.functions.scaleup = mock.Mock(return_value=None)

    def test_function_scaleup_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_scaleup_required_options(self):
        function_id = self._functions[0].id
        arglist = [function_id]
        verifylist = [('function', function_id), ('count', 1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.scaleup.assert_called_once_with(function_id, 1)

    def test_function_scaleup_all_options(self):
        function_id = self._functions[0].id
        count = 3
        arglist = [function_id, '--count', str(count)]
        verifylist = [('function', function_id), ('count', count)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.scaleup.assert_called_once_with(function_id,
                                                              count)

    def test_function_scaleup_worker_count_not_int(self):
        function_id = self._functions[0].id
        arglist = [function_id, '--count', 'NOT_INTEGER']
        verifylist = [('function_id', function_id), ('count', 'NOT_INTEGER')]

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Worker count must be a positive integer\.$',
            self.check_parser,
            self.cmd, arglist, verifylist)

    def test_function_scaleup_worker_count_zero(self):
        function_id = self._functions[0].id
        arglist = [function_id, '--count', '0']
        verifylist = [('function_id', function_id), ('count', 0)]

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Worker count must be a positive integer\.$',
            self.check_parser,
            self.cmd, arglist, verifylist)

    def test_function_scaleup_exception(self):
        function_id = self._functions[0].id
        self.client.functions.scaleup = mock.Mock(side_effect=RuntimeError)

        arglist = [function_id]
        verifylist = [('function', function_id), ('count', 1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to scale up the specified function\.$',
            self.cmd.take_action, parsed_args)

        self.client.functions.scaleup.assert_called_once_with(function_id, 1)


class TestScaledownFunction(TestFunction):

    def setUp(self):
        super(TestScaledownFunction, self).setUp()
        self.cmd = function.Scaledown(self.app, None)
        self.client.functions.scaledown = mock.Mock(return_value=None)

    def test_function_scaledown_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_scaledown_required_options(self):
        function_id = self._functions[0].id
        arglist = [function_id]
        verifylist = [('function', function_id), ('count', 1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.scaledown.assert_called_once_with(function_id, 1)

    def test_function_scaledown_all_options(self):
        function_id = self._functions[0].id
        count = 3
        arglist = [function_id, '--count', str(count)]
        verifylist = [('function', function_id), ('count', 3)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.functions.scaledown.assert_called_once_with(function_id,
                                                                count)

    def test_function_scaledown_exception(self):
        function_id = self._functions[0].id
        self.client.functions.scaledown = mock.Mock(side_effect=RuntimeError)

        arglist = [function_id]
        verifylist = [('function', function_id), ('count', 1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to scale down the specified function\.$',
            self.cmd.take_action, parsed_args)

        self.client.functions.scaledown.assert_called_once_with(function_id, 1)
