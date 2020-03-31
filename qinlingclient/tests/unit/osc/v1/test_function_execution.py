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
from qinlingclient.osc.v1 import function_execution
from qinlingclient.tests.unit.osc.v1 import fakes


class TestFunctionExecution(fakes.TestQinlingClient):

    def setUp(self):
        super(TestFunctionExecution, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.EXECUTION_COLUMNS
        self.data = []

        self._executions = fakes.FakeExecution.create_executions(count=3)
        for e in self._executions:
            self.data.append((e.id, e.function_alias, e.function_id,
                              e.function_version, e.description, e.input,
                              e.result, e.status, e.sync, e.project_id,
                              e.created_at, e.updated_at))


class TestListFunctionExecution(TestFunctionExecution):

    def setUp(self):
        super(TestListFunctionExecution, self).setUp()
        self.cmd = function_execution.List(self.app, None)

        self.columns = [c.capitalize() for c in base.EXECUTION_COLUMNS]

        self.client.function_executions.list = mock.Mock(
            return_value=self._executions)

    def test_function_execution_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_execution_list_with_filter(self):
        arglist = ['--filter', 'description=has:execution',
                   '--filter', 'status=eq:success']
        verifylist = [
            ('filters', ['description=has:execution', 'status=eq:success'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.list.assert_called_once_with(
            description='has:execution', status='eq:success'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_function_execution_list_with_invalid_filter(self):
        arglist = ['--filter', 'function_id']
        verifylist = [
            ('filters', ['function_id'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            ValueError,
            '^Invalid filter: function_id$',
            self.cmd.take_action, parsed_args
        )


class TestCreateFunctionExecution(TestFunctionExecution):

    def setUp(self):
        super(TestCreateFunctionExecution, self).setUp()
        self.cmd = function_execution.Create(self.app, None)

    def _create_fake_execution(self, attrs=None):
        # Allow to fake different create results
        e = fakes.FakeExecution.create_one_execution(attrs)
        self.client.function_executions.create = mock.Mock(return_value=e)
        data = (e.id, e.function_alias, e.function_id, e.function_version,
                e.description, e.input, e.result, e.status, e.sync,
                e.project_id, e.created_at, e.updated_at)
        return data

    def test_function_execution_create_function_id(self):
        """Create a function execution with function id."""
        function_id = self._executions[0].function_id
        attrs = {'function_id': function_id}
        created_data = self._create_fake_execution(attrs)

        arglist = ['--function', function_id]
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('function_alias', None),
            ('input', None),
            ('sync', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.create.assert_called_once_with(
            **{'function_alias': None,
               'function_id': function_id,
               'function_version': 0,
               'sync': True,
               'input': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_execution_create_function_name(self):
        """Create a function execution.

        1. use function name to find the function_id,
        2. all optional params are specified.
        """
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        function_version = 1
        function_input = '{"JSON_INPUT_KEY": "JSON_INPUT_VALUE"}'
        is_sync = False
        attrs = {'function_id': function_id,
                 'function_version': function_version,
                 'input': function_input,
                 'sync': is_sync}
        created_data = self._create_fake_execution(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = ['--function', function_name, '--function-version',
                   str(function_version), '--input', function_input, '--async']
        verifylist = [
            ('function', function_name),
            ('function_version', function_version),
            ('function_alias', None),
            ('input', function_input),
            ('sync', is_sync),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.create.assert_called_once_with(
            **{'function_alias': None,
               'function_id': function_id,
               'function_version': function_version,
               'sync': is_sync,
               'input': function_input}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)

    def test_function_execution_create_function_alias(self):
        """Create a function execution with function alias."""
        function_alias = 'fake_alias'
        function_input = '{"JSON_INPUT_KEY": "JSON_INPUT_VALUE"}'
        is_sync = False
        attrs = {'function_alias': function_alias,
                 'input': function_input,
                 'sync': is_sync}
        created_data = self._create_fake_execution(attrs)

        arglist = ['--function-alias', function_alias,
                   '--input', function_input, '--async']
        verifylist = [
            ('function', None),
            ('function_version', 0),
            ('function_alias', function_alias),
            ('input', function_input),
            ('sync', is_sync),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.create.assert_called_once_with(
            **{'function_alias': function_alias,
               'function_id': None,
               'function_version': None,
               'input': function_input,
               'sync': is_sync}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_function_execution_create_sync_async_mutually_exclusive(self):
        function_id = self._executions[0].function_id
        # --sync and --async are mutually exclusive
        arglist = ['--function', function_id, '--sync', '--async']
        verifylist = [
            ('function', self._executions[0].function_id),
            ('function_version', 0),
            ('input', None),
            ('sync', True),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_execution_create_version_not_integer(self):
        # function_version should be an integer value
        function_id = self._executions[0].function_id
        arglist = ['--function', function_id,
                   '--function-version', 'NOT_A_INTEGER']
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('input', None),
            ('sync', True),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDeleteFunctionExecution(TestFunctionExecution):

    def setUp(self):
        super(TestDeleteFunctionExecution, self).setUp()
        self.cmd = function_execution.Delete(self.app, None)
        self.client.function_executions.delete = mock.Mock(return_value=None)

    def test_function_execution_delete_no_option(self):
        # Unlike other resources, function_execution.Delete does nothing when
        # no arguments are specified.
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_executions.delete.assert_not_called()

    def test_function_execution_delete_one(self):
        execution_id = self._executions[0].id
        arglist = ['--execution', execution_id]
        verifylist = [('execution', [execution_id]), ('function', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_executions.delete.assert_called_once_with(
            execution_id
        )

    def test_function_execution_delete_multiple(self):
        execution_ids = [e.id for e in self._executions]
        arglist = ['--execution'] + execution_ids
        verifylist = [('execution', execution_ids), ('function', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(e_id) for e_id in execution_ids]
        self.assertEqual(len(execution_ids),
                         self.client.function_executions.delete.call_count)
        self.client.function_executions.delete.assert_has_calls(calls)

    def test_function_execution_delete_multiple_exception(self):
        execution_ids = [e.id for e in self._executions]
        arglist = ['--execution'] + execution_ids
        verifylist = [('execution', execution_ids), ('function', None)]

        self.client.function_executions.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            r'^Unable to delete the specified execution\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deletion failed, but the third is done normally
        calls = [mock.call(e_id) for e_id in execution_ids]
        self.assertEqual(len(execution_ids),
                         self.client.function_executions.delete.call_count)
        self.client.function_executions.delete.assert_has_calls(calls)

    def test_function_execution_delete_by_function_id(self):
        execution_id = self._executions[0].id
        function_id = self._executions[0].function_id

        self.client.function_executions.list.return_value = [
            self._executions[0]
        ]

        arglist = ['--function', function_id]
        verifylist = [('execution', None), ('function', [function_id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_executions.delete.assert_called_once_with(
            execution_id
        )
        self.client.function_executions.list.assert_called_once_with(
            function_id=function_id
        )

    def test_function_execution_delete_execution_function_mutually_exclusive(
            self
    ):
        # --execution and --function are mutually exclusive
        execution_id = self._executions[0].id
        function_id = self._executions[0].function_id

        arglist = ['--execution', execution_id, '--function', function_id]
        verifylist = [('execution', [execution_id]),
                      ('function', [function_id])]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestShowFunctionExecution(TestFunctionExecution):

    def setUp(self):
        super(TestShowFunctionExecution, self).setUp()
        self.cmd = function_execution.Show(self.app, None)
        self.client.function_executions.get = mock.Mock(
            return_value=self._executions[0]
        )

    def test_function_execution_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_execution_show(self):
        execution_id = self._executions[0].id
        arglist = [execution_id]
        verifylist = [('execution', execution_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_executions.get.assert_called_once_with(
            execution_id
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestLogShowFunctionExecution(TestFunctionExecution):

    def setUp(self):
        super(TestLogShowFunctionExecution, self).setUp()
        self.cmd = function_execution.LogShow(self.app, None)
        self.app_stdout_write = mock.Mock()
        self.app.stdout.write = self.app_stdout_write

    def test_function_execution_log_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_execution_log_show(self):
        execution_id = self._executions[0].id
        fake_log = 'This is a fake log of an execution.'

        self.client.function_executions.get_log.return_value = fake_log

        arglist = [execution_id]
        verifylist = [('execution', execution_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_executions.get_log.assert_called_once_with(
            execution_id
        )
        self.app_stdout_write.assert_called_once_with(fake_log)

    def test_function_execution_log_show_empty_log(self):
        execution_id = self._executions[0].id

        self.client.function_executions.get_log.return_value = ''

        arglist = [execution_id]
        verifylist = [('execution', execution_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.function_executions.get_log.assert_called_once_with(
            execution_id
        )
        self.app_stdout_write.assert_called_once_with("\n")
