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
from qinlingclient.osc.v1 import webhook
from qinlingclient.tests.unit.osc.v1 import fakes


class TestWebhook(fakes.TestQinlingClient):

    def setUp(self):
        super(TestWebhook, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.WEBHOOK_COLUMNS
        self.data = []

        self._webhooks = fakes.FakeWebhook.create_webhooks(count=3)
        for w in self._webhooks:
            self.data.append((w.id, w.function_id, w.function_version,
                              w.description, w.project_id,
                              w.created_at, w.updated_at,
                              w.webhook_url))


class TestListWebhook(TestWebhook):

    def setUp(self):
        super(TestListWebhook, self).setUp()
        self.cmd = webhook.List(self.app, None)

        self.columns = [c.capitalize() for c in base.WEBHOOK_COLUMNS]

        self.client.webhooks.list = mock.Mock(return_value=self._webhooks)

    def test_webhook_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_webhook_list_with_filter(self):
        arglist = ['--filter', 'function_version=neq:0',
                   '--filter', 'description=has:webhook']
        verifylist = [
            ('filters', ['function_version=neq:0', 'description=has:webhook']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.list.assert_called_once_with(
            function_version='neq:0', description='has:webhook'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_webhook_list_with_invalid_filter(self):
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


class TestCreateWebhook(TestWebhook):

    def setUp(self):
        super(TestCreateWebhook, self).setUp()
        self.cmd = webhook.Create(self.app, None)

    def _create_fake_webhook(self, attrs=None):
        # Allow to fake different create results
        w = fakes.FakeWebhook.create_one_webhook(attrs)
        self.client.webhooks.create = mock.Mock(return_value=w)
        data = (w.id, w.function_id, w.function_version, w.description,
                w.project_id, w.created_at, w.updated_at, w.webhook_url)
        return data

    def test_webhook_create_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_webhook_create_required_options(self):
        """Create a webhook.

        1. use function_id,
        2. all other params except the required ones are not set.
        """
        function_id = self._webhooks[0].function_id
        attrs = {'function_id': function_id}
        created_data = self._create_fake_webhook(attrs)

        arglist = [function_id]
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('description', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.create.assert_called_once_with(
            **{'function_id': function_id,
               'function_version': 0,
               'description': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_webhook_create_all_options(self):
        """Create a webhook.

        1. use function name to find the function_id,
        2. all optional params are specified.
        """
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        function_version = 1
        webhook_description = 'This is a newly created webhook.'
        attrs = {'function_id': function_id,
                 'function_version': function_version,
                 'description': webhook_description}
        created_data = self._create_fake_webhook(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = [function_name,
                   '--function-version', str(function_version),
                   '--description', webhook_description]
        verifylist = [
            ('function', function_name),
            ('function_version', function_version),
            ('description', webhook_description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.create.assert_called_once_with(
            **{'function_id': function_id,
               'function_version': function_version,
               'description': webhook_description}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)

    def test_webhook_create_version_not_integer(self):
        # function_version should be an integer value
        function_id = self._webhooks[0].function_id

        arglist = [function_id, '--function-version', 'NOT_A_INTEGER']
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('description', None),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDeleteWebhook(TestWebhook):

    def setUp(self):
        super(TestDeleteWebhook, self).setUp()
        self.cmd = webhook.Delete(self.app, None)
        self.client.webhooks.delete = mock.Mock(return_value=None)

    def test_webhook_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_webhook_delete_one(self):
        webhook_id = self._webhooks[0].id
        arglist = [webhook_id]
        verifylist = [('webhook', [webhook_id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.webhooks.delete.assert_called_once_with(webhook_id)

    def test_webhook_delete_multiple(self):
        webhook_ids = [w.id for w in self._webhooks]
        arglist = webhook_ids
        verifylist = [('webhook', webhook_ids)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(w_id) for w_id in webhook_ids]
        self.assertEqual(len(webhook_ids),
                         self.client.webhooks.delete.call_count)
        self.client.webhooks.delete.assert_has_calls(calls)

    def test_webhook_delete_multiple_exception(self):
        webhook_ids = [w.id for w in self._webhooks]
        arglist = webhook_ids
        verifylist = [('webhook', webhook_ids)]

        self.client.webhooks.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to delete the specified webhook\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deleteion failed, but the third is done normally
        calls = [mock.call(w_id) for w_id in webhook_ids]
        self.assertEqual(len(webhook_ids),
                         self.client.webhooks.delete.call_count)
        self.client.webhooks.delete.assert_has_calls(calls)


class TestShowWebhook(TestWebhook):

    def setUp(self):
        super(TestShowWebhook, self).setUp()
        self.cmd = webhook.Show(self.app, None)
        self.client.webhooks.get = mock.Mock(return_value=self._webhooks[0])

    def test_webhook_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_webhook_show(self):
        webhook_id = self._webhooks[0].id
        arglist = [webhook_id]
        verifylist = [('webhook', webhook_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.get.assert_called_once_with(webhook_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestUpdateWebhook(TestWebhook):

    def setUp(self):
        super(TestUpdateWebhook, self).setUp()
        self.cmd = webhook.Update(self.app, None)

    def _update_fake_webhook(self, attrs=None):
        # Allow to fake different update results
        w = fakes.FakeWebhook.create_one_webhook(attrs)
        self.client.webhooks.update = mock.Mock(return_value=w)
        data = (w.id, w.function_id, w.function_version, w.description,
                w.project_id, w.created_at, w.updated_at, w.webhook_url)
        return data

    def test_webhook_update_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_webhook_update_required_options(self):
        """Update a webhook.

        Do nothing as only the webhook id is specified.
        """
        webhook_id = self._webhooks[0].id
        attrs = {'id': webhook_id}
        updated_data = self._update_fake_webhook(attrs)

        arglist = [webhook_id]
        verifylist = [
            ('id', webhook_id),
            ('function_id', None),
            ('function_version', 0),
            ('description', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.update.assert_called_once_with(
            webhook_id,
            **{'function_id': None,
               'function_version': 0,
               'description': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_webhook_update_all_options(self):
        webhook_id = self._webhooks[0].id
        function_id = self._webhooks[1].function_id
        function_version = 1
        webhook_description = 'This is a updated webhook.'
        attrs = {'id': webhook_id, 'function_id': function_id,
                 'function_version': function_version,
                 'description': webhook_description}
        updated_data = self._update_fake_webhook(attrs)

        arglist = [webhook_id, '--function-id', function_id,
                   '--function-version', str(function_version),
                   '--description', webhook_description]
        verifylist = [
            ('id', webhook_id),
            ('function_id', function_id),
            ('function_version', 1),
            ('description', webhook_description),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.webhooks.update.assert_called_once_with(
            webhook_id,
            **{'function_id': function_id,
               'function_version': 1,
               'description': webhook_description}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_webhook_update_version_not_integer(self):
        # function_version should be an integer value
        webhook_id = self._webhooks[0].id

        arglist = [webhook_id, '--function-version', 'NOT_A_INTEGER']
        verifylist = [
            ('id', webhook_id),
            ('function', None),
            ('function_version', 0),
            ('description', None),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
