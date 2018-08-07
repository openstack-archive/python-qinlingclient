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

from qinlingclient.osc.v1 import base
from qinlingclient.osc.v1 import function_worker
from qinlingclient.tests.unit.osc.v1 import fakes


class TestFunctionWorker(fakes.TestQinlingClient):

    def setUp(self):
        super(TestFunctionWorker, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.WORKER_COLUMNS
        self.data = []

        workers = fakes.FakeFunctionWorker.create_function_workers(count=3)
        self._function_workers = workers
        for w in self._function_workers:
            self.data.append((w.function_id, w.worker_name))


class TestListFunctionWorker(TestFunctionWorker):

    def setUp(self):
        super(TestListFunctionWorker, self).setUp()
        self.cmd = function_worker.List(self.app, None)

        self.columns = [c.capitalize() for c in base.WORKER_COLUMNS]

        self.client.function_workers.list = mock.Mock(
            return_value=self._function_workers)

    def test_function_worker_list_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_function_worker_list(self):
        function_id = self._function_workers[0].function_id

        arglist = [function_id]
        verifylist = [('function', function_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.function_workers.list.assert_called_once_with(function_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))
