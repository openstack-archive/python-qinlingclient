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

from unittest import mock

from osc_lib.tests import utils as osc_tests_utils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient.osc.v1 import runtime
from qinlingclient.tests.unit.osc.v1 import fakes


class TestRuntime(fakes.TestQinlingClient):

    def setUp(self):
        super(TestRuntime, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.RUNTIME_COLUMNS
        self.data = []

        self._runtimes = fakes.FakeRuntime.create_runtimes(count=3)
        for r in self._runtimes:
            self.data.append((r.id, r.name, r.image, r.status, r.description,
                              r.is_public, r.trusted, r.project_id,
                              r.created_at, r.updated_at))


class TestListRuntime(TestRuntime):

    def setUp(self):
        super(TestListRuntime, self).setUp()
        self.cmd = runtime.List(self.app, None)

        self.columns = [c.capitalize() for c in base.RUNTIME_COLUMNS]

        self.client.runtimes.list = mock.Mock(return_value=self._runtimes)

    def test_runtime_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_runtime_list_with_filter(self):
        arglist = ['--filter', 'name=has:runtime',
                   '--filter', 'status=eq:available']
        verifylist = [
            ('filters', ['name=has:runtime', 'status=eq:available'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.list.assert_called_once_with(
            name='has:runtime', status='eq:available'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_runtime_list_with_invalid_filter(self):
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


class TestCreateRuntime(TestRuntime):

    def setUp(self):
        super(TestCreateRuntime, self).setUp()
        self.cmd = runtime.Create(self.app, None)

    def _create_fake_runtime(self, attrs=None):
        # Allow to fake different create results
        r = fakes.FakeRuntime.create_one_runtime(attrs)
        self.client.runtimes.create = mock.Mock(return_value=r)
        data = (r.id, r.name, r.image, r.status, r.description,
                r.is_public, r.trusted, r.project_id,
                r.created_at, r.updated_at)
        return data

    def test_runtime_create_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_runtime_create_required_options(self):
        image = 'specified-image-name'
        attrs = {'image': image}
        created_data = self._create_fake_runtime(attrs)

        arglist = [image]
        verifylist = [
            ('image', image),
            ('name', None),
            ('description', None),
            ('trusted', True),
            ('is_public', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.create.assert_called_once_with(**{
            'name': None,
            'description': None,
            'image': image,
            'trusted': True,
            'is_public': True,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_runtime_create_all_options(self):
        image = 'specified-image-name'
        name = 'specified-runtime-name'
        description = 'specified-runtime-description'
        trusted = False
        is_public = False
        attrs = {'image': image, 'name': name,
                 'description': description, 'trusted': trusted,
                 'is_public': is_public}
        created_data = self._create_fake_runtime(attrs)

        arglist = [
            '--name', name,
            '--description', description,
            '--untrusted',
            '--private',
            image,
        ]
        verifylist = [
            ('image', image),
            ('name', name),
            ('description', description),
            ('trusted', trusted),
            ('is_public', is_public)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.create.assert_called_once_with(**{
            'name': name,
            'description': description,
            'image': image,
            'trusted': trusted,
            'is_public': is_public,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)


class TestDeleteRuntime(TestRuntime):

    def setUp(self):
        super(TestDeleteRuntime, self).setUp()
        self.cmd = runtime.Delete(self.app, None)
        self.client.runtimes.delete = mock.Mock(return_value=None)

    def test_runtime_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_runtime_delete_one(self):
        runtime_id = self._runtimes[0].id
        arglist = [runtime_id]
        verifylist = [('runtime', [runtime_id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.runtimes.delete.assert_called_once_with(runtime_id)

    def test_runtime_delete_multiple(self):
        runtime_ids = [r.id for r in self._runtimes]
        arglist = runtime_ids
        verifylist = [('runtime', runtime_ids)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(r_id) for r_id in runtime_ids]
        self.assertEqual(len(runtime_ids),
                         self.client.runtimes.delete.call_count)
        self.client.runtimes.delete.assert_has_calls(calls)

    def test_runtime_delete_multiple_exception(self):
        runtime_ids = [r.id for r in self._runtimes]
        arglist = runtime_ids
        verifylist = [('runtime', runtime_ids)]

        self.client.runtimes.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            r'^Unable to delete the specified runtime\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deletion failed, but the third is done normally
        calls = [mock.call(r_id) for r_id in runtime_ids]
        self.assertEqual(len(runtime_ids),
                         self.client.runtimes.delete.call_count)
        self.client.runtimes.delete.assert_has_calls(calls)


class TestShowRuntime(TestRuntime):

    def setUp(self):
        super(TestShowRuntime, self).setUp()
        self.cmd = runtime.Show(self.app, None)
        self.client.runtimes.get = mock.Mock(return_value=self._runtimes[0])

    def test_runtime_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_runtime_show(self):
        runtime_id = self._runtimes[0].id
        arglist = [runtime_id]
        verifylist = [('runtime', runtime_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.get.assert_called_once_with(runtime_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestShowRuntimePool(TestRuntime):

    def setUp(self):
        super(TestShowRuntimePool, self).setUp()
        self.cmd = runtime.Pool(self.app, None)

        self.columns = base.RUNTIME_POOL_COLUMNS
        pool_attrs = {'name': self._runtimes[0].id}
        pool = fakes.FakeRuntime.create_one_runtime_pool(pool_attrs)
        self.pool_data = (pool.name, pool.capacity)

        self.client.runtimes.get_pool = mock.Mock(return_value=pool)

    def test_runtime_pool_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_runtime_pool_show(self):
        runtime_id = self._runtimes[0].id
        arglist = [runtime_id]
        verifylist = [('runtime', runtime_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.runtimes.get_pool.assert_called_once_with(runtime_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.pool_data, data)
