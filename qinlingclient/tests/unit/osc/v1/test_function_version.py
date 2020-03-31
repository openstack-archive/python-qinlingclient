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

from osc_lib.tests import utils as osc_tests_utils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient.osc.v1 import function_version
from qinlingclient.tests.unit.osc.v1 import fakes


class TestFunctionVersion(fakes.TestQinlingClient):

    def setUp(self):
        super(TestFunctionVersion, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.FUNCTION_VERSION_COLUMNS
        self.data = []

        versions = fakes.FakeFunctionVersion.create_function_versions(count=3)
        self._function_versions = versions
        for v in self._function_versions:
            self.data.append((v.id, v.function_id, v.description,
                              v.version_number, v.count, v.project_id,
                              v.created_at, v.updated_at))


class TestListFunctionVersion(TestFunctionVersion):

    def setUp(self):
        super(TestListFunctionVersion, self).setUp()
        self.cmd = function_version.List(self.app, None)

        self.columns = [c.capitalize() for c in base.FUNCTION_VERSION_COLUMNS]

        self.client.function_versions.list = mock.Mock(
            return_value=self._function_versions)

    def test_function_version_list_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_version_list(self):
        function_id = self._function_versions[0].function_id

        arglist = [function_id]
        verifylist = [('function_id', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_versions.list.assert_called_once_with(function_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestCreateFunctionVersion(TestFunctionVersion):

    def setUp(self):
        super(TestCreateFunctionVersion, self).setUp()
        self.cmd = function_version.Create(self.app, None)

    def _create_fake_function_version(self, attrs=None):
        # Allow to fake different create results
        v = fakes.FakeFunctionVersion.create_one_function_version(attrs)
        self.client.function_versions.create = mock.Mock(return_value=v)
        data = (v.id, v.function_id, v.description,
                v.version_number, v.count, v.project_id,
                v.created_at, v.updated_at)
        return data

    def test_function_version_create_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_version_create_required_options(self):
        """Create a function version.

        1. use function_id,
        2. all other params except the required ones are not set.
        """
        function_id = self._function_versions[0].function_id
        attrs = {'function_id': function_id, 'version_number': '2'}
        created_data = self._create_fake_function_version(attrs)

        arglist = [function_id]
        verifylist = [
            ('function', function_id),
            ('description', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_versions.create.assert_called_once_with(
            function_id, description=None
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_version_create_all_options(self):
        """Create a function version.

        1. use function name to find the function_id,
        2. all optional params are specified.
        """
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        description = 'This is a new function version.'
        attrs = {'function_id': function_id,
                 'description': description,
                 'version_number': '2'}
        created_data = self._create_fake_function_version(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = [function_name, '--description', description]
        verifylist = [
            ('function', function_name),
            ('description', description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_versions.create.assert_called_once_with(
            function_id, description=description
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)


class TestDeleteFunctionVersion(TestFunctionVersion):

    def setUp(self):
        super(TestDeleteFunctionVersion, self).setUp()
        self.cmd = function_version.Delete(self.app, None)
        self.client.function_versions.delete = mock.Mock(return_value=None)

    def test_function_version_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_version_delete(self):
        function_id = self._function_versions[0].function_id
        version_number = str(self._function_versions[0].version_number)

        arglist = [function_id, version_number]
        verifylist = [
            ('function_id', function_id),
            ('version_number', version_number),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_versions.delete.assert_called_once_with(
            function_id, version_number
        )


class TestShowFunctionVersion(TestFunctionVersion):

    def setUp(self):
        super(TestShowFunctionVersion, self).setUp()
        self.cmd = function_version.Show(self.app, None)
        self.client.function_versions.get = mock.Mock(
            return_value=self._function_versions[0]
        )

    def test_function_version_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_version_show(self):
        function_id = self._function_versions[0].function_id
        version_number = str(self._function_versions[0].version_number)

        arglist = [function_id, version_number]
        verifylist = [
            ('function_id', function_id),
            ('version_number', version_number),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_versions.get.assert_called_once_with(
            function_id, version_number
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestDetachFunctionVersion(TestFunctionVersion):

    def setUp(self):
        super(TestDetachFunctionVersion, self).setUp()
        self.cmd = function_version.Detach(self.app, None)
        self.client.function_versions.detach = mock.Mock(return_value=None)

    def test_function_version_detach_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_version_detach(self):
        function_id = self._function_versions[0].function_id
        version_number = str(self._function_versions[0].version_number)

        arglist = [function_id, version_number]
        verifylist = [
            ('function_id', function_id),
            ('version_number', version_number),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_versions.detach.assert_called_once_with(
            function_id, version_number
        )

    def test_function_version_detach_exception(self):
        function_id = self._function_versions[0].function_id
        version_number = str(self._function_versions[0].version_number)

        self.client.function_versions.detach = mock.Mock(
            side_effect=RuntimeError
        )

        arglist = [function_id, version_number]
        verifylist = [
            ('function_id', function_id),
            ('version_number', version_number),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            r'^Unable to detach the specified function version\.$',
            self.cmd.take_action, parsed_args)

        self.client.function_versions.detach.assert_called_once_with(
            function_id, version_number
        )
