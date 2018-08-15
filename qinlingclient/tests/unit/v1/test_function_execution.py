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

import json
import uuid

from qinlingclient.common import exceptions
from qinlingclient.tests.unit.v1 import test_client

EXECUTION_1 = {'id': str(uuid.uuid4()), 'function_id': str(uuid.uuid4())}
EXECUTION_2 = {'id': str(uuid.uuid4()), 'function_id': str(uuid.uuid4())}

LIST_FUNCTION_EXECUTIONS_RESP = {
    'executions': [EXECUTION_1, EXECUTION_2]
}


class TestFunctionExecution(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_function_execution(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/executions',
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTION_EXECUTIONS_RESP,
            status_code=200
        )
        ret = self.client.function_executions.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [EXECUTION_1, EXECUTION_2],
            [resource.to_dict() for resource in ret])

    def test_list_function_execution_with_params(self):
        self.requests_mock.register_uri(
            'GET',
            (test_client.QINLING_URL +
             '/v1/executions?status=success&sync=True'),
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTION_EXECUTIONS_RESP,
            status_code=200
        )
        ret = self.client.function_executions.list(status='success', sync=True)
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [EXECUTION_1, EXECUTION_2],
            [resource.to_dict() for resource in ret])

    def test_create_function_execution(self):
        function_id = EXECUTION_1['function_id']
        request_data = {'function_id': function_id, 'function_version': 0,
                        'sync': True, 'input': None}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/executions',
            headers={'Content-Type': 'application/json'},
            json=EXECUTION_1,
            status_code=201
        )
        ret = self.client.function_executions.create(function_id)
        self.assertEqual(EXECUTION_1, ret.to_dict())
        self.assertEqual(json.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_execution_all_options(self):
        function_id = EXECUTION_1['function_id']
        function_version = 1
        sync = False
        function_input = '{"name": "Qinling"}'
        request_data = {'function_id': function_id,
                        'function_version': function_version,
                        'sync': sync, 'input': function_input}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/executions',
            headers={'Content-Type': 'application/json'},
            json=EXECUTION_1,
            status_code=201
        )
        ret = self.client.function_executions.create(
            function_id, version=function_version, sync=sync,
            input=function_input)
        self.assertEqual(EXECUTION_1, ret.to_dict())
        self.assertEqual(json.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_execution_error(self):
        function_id = EXECUTION_1['function_id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/executions',
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.function_executions.create,
            function_id)

    def test_delete_function_execution(self):
        execution_id = EXECUTION_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/executions/%s' % execution_id,
            status_code=204
        )
        ret = self.client.function_executions.delete(execution_id)
        self.assertIsNone(ret)

    def test_delete_function_execution_error(self):
        execution_id = EXECUTION_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/executions/%s' % execution_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_executions.delete,
            execution_id
        )

    def test_get_function_execution(self):
        execution_id = EXECUTION_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/executions/%s' % execution_id,
            headers={'Content-Type': 'application/json'},
            json=EXECUTION_2,
            status_code=200
        )
        ret = self.client.function_executions.get(execution_id)
        self.assertEqual(EXECUTION_2, ret.to_dict())

    def test_get_function_execution_error(self):
        execution_id = EXECUTION_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/executions/%s' % execution_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_executions.get,
            execution_id
        )

    def test_get_function_execution_log(self):
        execution_id = EXECUTION_2['id']
        execution_log = 'Preparing...\nRunning...\nDone.'
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/executions/%s/log' % execution_id,
            text=execution_log,
            headers={'Content-Type': 'text/plain'},
            status_code=200
        )
        ret = self.client.function_executions.get_log(execution_id)
        self.assertEqual(execution_log, ret)

    def test_get_function_execution_log_error(self):
        execution_id = EXECUTION_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/executions/%s/log' % execution_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_executions.get_log,
            execution_id
        )
