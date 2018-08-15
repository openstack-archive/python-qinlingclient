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

ALIAS_1 = {'name': 'function_alias_1', 'function_id': str(uuid.uuid4())}
ALIAS_2 = {'name': 'function_alias_2', 'function_id': str(uuid.uuid4())}

LIST_FUNCTION_ALIASES_RESP = {
    'function_aliases': [ALIAS_1, ALIAS_2]
}


class TestFunctionAlias(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_function_alias(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/aliases',
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTION_ALIASES_RESP,
            status_code=200
        )
        ret = self.client.function_aliases.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [ALIAS_1, ALIAS_2],
            [resource.to_dict() for resource in ret])

    def test_create_function_alias(self):
        name = ALIAS_1['name']
        function_id = ALIAS_1['function_id']
        request_data = {'name': name, 'function_id': function_id,
                        'function_version': 0, 'description': ''}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/aliases',
            headers={'Content-Type': 'application/json'},
            json=ALIAS_1,
            status_code=201
        )
        ret = self.client.function_aliases.create(name, function_id)
        self.assertEqual(ALIAS_1, ret.to_dict())
        self.assertEqual(json.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_alias_all_options(self):
        name = ALIAS_1['name']
        function_id = ALIAS_1['function_id']
        function_version = 1
        description = 'A newly created function alias.'
        request_data = {'name': name, 'function_id': function_id,
                        'function_version': function_version,
                        'description': description}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/aliases',
            headers={'Content-Type': 'application/json'},
            json=ALIAS_1,
            status_code=201
        )
        ret = self.client.function_aliases.create(
            name, function_id, function_version=function_version,
            description=description
        )
        self.assertEqual(ALIAS_1, ret.to_dict())
        self.assertEqual(json.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_alias_error(self):
        name = ALIAS_1['name']
        function_id = ALIAS_1['function_id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/aliases',
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.function_aliases.create,
            name, function_id)

    def test_delete_function_alias(self):
        name = ALIAS_1['name']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            status_code=204
        )
        ret = self.client.function_aliases.delete(name)
        self.assertIsNone(ret)

    def test_delete_function_alias_error(self):
        name = ALIAS_1['name']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_aliases.delete,
            name
        )

    def test_get_function_alias(self):
        name = ALIAS_2['name']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            headers={'Content-Type': 'application/json'},
            json=ALIAS_2,
            status_code=200
        )
        ret = self.client.function_aliases.get(name)
        self.assertEqual(ALIAS_2, ret.to_dict())

    def test_get_function_alias_error(self):
        name = ALIAS_2['name']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_aliases.get,
            name
        )

    def test_update_function_alias(self):
        name = ALIAS_2['name']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            headers={'Content-Type': 'application/json'},
            json=ALIAS_2,
            status_code=200
        )
        ret = self.client.function_aliases.update(name)
        self.assertEqual(ALIAS_2, ret.to_dict())

    def test_update_function_alias_all_options(self):
        name = ALIAS_2['name']
        function_id = ALIAS_2['function_id']
        function_version = 2
        description = 'An updated function alias.'
        request_data = {'function_id': function_id,
                        'function_version': function_version,
                        'description': description}
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            headers={'Content-Type': 'application/json'},
            json=ALIAS_2,
            status_code=200
        )
        ret = self.client.function_aliases.update(
            name, function_id=function_id, function_version=function_version,
            description=description
        )
        self.assertEqual(ALIAS_2, ret.to_dict())
        self.assertEqual(json.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_update_function_alias_error(self):
        name = ALIAS_2['name']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/aliases/%s' % name,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_aliases.update,
            name)
