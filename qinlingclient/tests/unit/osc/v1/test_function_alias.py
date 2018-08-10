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
from qinlingclient.osc.v1 import function_alias
from qinlingclient.tests.unit.osc.v1 import fakes


class TestFunctionAlias(fakes.TestQinlingClient):

    def setUp(self):
        super(TestFunctionAlias, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.FUNCTION_ALIAS_COLUMNS
        self.data = []

        aliases = fakes.FakeFunctionAlias.create_function_aliases(count=3)
        self._function_aliases = aliases
        for a in self._function_aliases:
            self.data.append((a.name, a.function_id, a.description,
                              a.function_version, a.project_id,
                              a.created_at, a.updated_at))


class TestListFunctionAlias(TestFunctionAlias):

    def setUp(self):
        super(TestListFunctionAlias, self).setUp()
        self.cmd = function_alias.List(self.app, None)

        self.columns = [c.capitalize() for c in base.FUNCTION_ALIAS_COLUMNS]

        self.client.function_aliases.list = mock.Mock(
            return_value=self._function_aliases
        )

    def test_function_alias_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_alias_list_with_filter(self):
        arglist = ['--filter', 'name=has:alias',
                   '--filter', 'function_id=has:900dcafe']
        verifylist = [
            ('filters', ['name=has:alias', 'function_id=has:900dcafe']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.list.assert_called_once_with(
            name='has:alias', function_id='has:900dcafe'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_alias_list_with_invalid_filter(self):
        arglist = ['--filter', 'function_version']
        verifylist = [
            ('filters', ['function_version']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            ValueError,
            '^Invalid filter: function_version$',
            self.cmd.take_action, parsed_args
        )


class TestCreateFunctionAlias(TestFunctionAlias):

    def setUp(self):
        super(TestCreateFunctionAlias, self).setUp()
        self.cmd = function_alias.Create(self.app, None)

    def _create_fake_function_alias(self, attrs=None):
        # Allow to fake different create results
        a = fakes.FakeFunctionAlias.create_one_function_alias(attrs)
        self.client.function_aliases.create = mock.Mock(return_value=a)
        data = (a.name, a.function_id, a.description, a.function_version,
                a.project_id, a.created_at, a.updated_at)
        return data

    def test_function_alias_create_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_alias_create_required_options(self):
        """Create a function alias.

        1. use function_id,
        2. all other params except the required ones are not set.
        """
        alias_name = 'FAKE_ALIAS_NAME'
        function_id = self._function_aliases[0].function_id
        attrs = {'name': alias_name, 'function_id': function_id}
        created_data = self._create_fake_function_alias(attrs)

        arglist = [alias_name, '--function', function_id]
        verifylist = [
            ('name', alias_name),
            ('function', function_id),
            ('function_version', 0),
            ('description', ''),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.create.assert_called_once_with(
            alias_name,
            **{'function_id': function_id,
               'function_version': 0,
               'description': ''}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_alias_create_all_options(self):
        """Create a function alias.

        1. use function name to find the function_id,
        2. all optional params are specified.
        """
        alias_name = 'FAKE_ALIAS_NAME'
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        function_version = 1
        alias_description = 'This is a newly created function alias.'
        attrs = {'name': alias_name,
                 'function_id': function_id,
                 'function_version': function_version,
                 'description': alias_description}
        created_data = self._create_fake_function_alias(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = [alias_name,
                   '--function', function_name,
                   '--function-version', str(function_version),
                   '--description', alias_description]
        verifylist = [
            ('name', alias_name),
            ('function', function_name),
            ('function_version', function_version),
            ('description', alias_description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.create.assert_called_once_with(
            alias_name,
            **{'function_id': function_id,
               'function_version': function_version,
               'description': alias_description}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)

    def test_function_alias_create_version_not_integer(self):
        # function_version should be an integer value
        alias_name = 'FAKE_ALIAS_NAME'
        function_id = self._function_aliases[0].function_id

        arglist = [alias_name,
                   '--function', function_id,
                   '--function-version', 'NOT_A_INTEGER']
        verifylist = [
            ('name', alias_name),
            ('function', function_id),
            ('function_version', 0),
            ('description', None),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDeleteFunctionAlias(TestFunctionAlias):

    def setUp(self):
        super(TestDeleteFunctionAlias, self).setUp()
        self.cmd = function_alias.Delete(self.app, None)
        self.client.function_aliases.delete = mock.Mock(return_value=None)

    def test_function_alias_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_alias_delete_one(self):
        alias_name = self._function_aliases[0].name
        arglist = [alias_name]
        verifylist = [('name', [alias_name])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_aliases.delete.assert_called_once_with(alias_name)

    def test_function_alias_delete_multiple(self):
        alias_names = [a.name for a in self._function_aliases]
        arglist = alias_names
        verifylist = [('name', alias_names)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(a_name) for a_name in alias_names]
        self.assertEqual(len(alias_names),
                         self.client.function_aliases.delete.call_count)
        self.client.function_aliases.delete.assert_has_calls(calls)

    def test_function_alias_delete_multiple_exception(self):
        alias_names = [a.name for a in self._function_aliases]
        arglist = alias_names
        verifylist = [('name', alias_names)]

        self.client.function_aliases.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to delete the specified function_alias\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deleteion failed, but the third is done normally
        calls = [mock.call(a_name) for a_name in alias_names]
        self.assertEqual(len(alias_names),
                         self.client.function_aliases.delete.call_count)
        self.client.function_aliases.delete.assert_has_calls(calls)


class TestShowFunctionAlias(TestFunctionAlias):

    def setUp(self):
        super(TestShowFunctionAlias, self).setUp()
        self.cmd = function_alias.Show(self.app, None)
        self.client.function_aliases.get = mock.Mock(
            return_value=self._function_aliases[0])

    def test_function_alias_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_alias_show(self):
        alias_name = self._function_aliases[0].name
        arglist = [alias_name]
        verifylist = [('name', alias_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.get.assert_called_once_with(alias_name)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestUpdateFunctionAlias(TestFunctionAlias):

    def setUp(self):
        super(TestUpdateFunctionAlias, self).setUp()
        self.cmd = function_alias.Update(self.app, None)

    def _update_fake_function_alias(self, attrs=None):
        # Allow to fake different update results
        a = fakes.FakeFunctionAlias.create_one_function_alias(attrs)
        self.client.function_aliases.update = mock.Mock(return_value=a)
        data = (a.name, a.function_id, a.description, a.function_version,
                a.project_id, a.created_at, a.updated_at)
        return data

    def test_function_alias_update_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_alias_update_required_options(self):
        """Update a function alias.

        Do nothing as only the alias name is specified.
        """
        alias_name = self._function_aliases[0].name
        attrs = {'name': alias_name}
        updated_data = self._update_fake_function_alias(attrs)

        arglist = [alias_name]
        verifylist = [
            ('name', alias_name),
            ('function', None),
            ('function_version', None),
            ('description', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.update.assert_called_once_with(
            alias_name,
            **{'function_id': None,
               'function_version': None,
               'description': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_function_alias_update_all_options(self):
        """Update a function alias.

        use function name to find the function_id,
        """
        alias_name = self._function_aliases[0].name
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        function_version = 1
        alias_description = 'This is a updated function alias.'
        attrs = {'name': alias_name,
                 'function_id': function_id,
                 'function_version': function_version,
                 'description': alias_description}
        created_data = self._update_fake_function_alias(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = [alias_name,
                   '--function', function_name,
                   '--function-version', str(function_version),
                   '--description', alias_description]
        verifylist = [
            ('name', alias_name),
            ('function', function_name),
            ('function_version', str(function_version)),
            ('description', alias_description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_aliases.update.assert_called_once_with(
            alias_name,
            **{'function_id': function_id,
               'function_version': str(function_version),
               'description': alias_description}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)
