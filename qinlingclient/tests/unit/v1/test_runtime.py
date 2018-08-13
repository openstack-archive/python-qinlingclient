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

RUNTIME_1 = {'id': str(uuid.uuid4()), 'name': 'runtime_1'}
RUNTIME_2 = {'id': str(uuid.uuid4()), 'name': 'runtime_2'}

LIST_RUNTIMES_RESP = {
    'runtimes': [RUNTIME_1, RUNTIME_2]
}

RUNTIME_POOL = {'name': RUNTIME_2['id'],
                'capacity': {'available': 5, 'total': 5}}


class TestRuntime(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_runtime(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/runtimes',
            headers={'Content-Type': 'application/json'},
            json=LIST_RUNTIMES_RESP,
            status_code=200
        )
        ret = self.client.runtimes.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [RUNTIME_1, RUNTIME_2],
            [resource.to_dict() for resource in ret])

    def test_create_runtime(self):
        image_name = 'image_name'
        request_data = {'image': image_name, 'trusted': True}

        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/runtimes',
            headers={'Content-Type': 'application/json'},
            json=RUNTIME_1,
            status_code=201
        )
        ret = self.client.runtimes.create(image_name)

        self.assertEqual(RUNTIME_1, ret.to_dict())
        self.assertEqual(request_data,
                         json.loads(self.requests_mock.last_request.text))

    def test_create_runtime_all_options(self):
        image_name = 'image_name'
        runtime_name = 'runtime_name'
        description = 'A newly created runtime.'
        trusted = False

        request_data = {'image': image_name, 'trusted': trusted,
                        'name': runtime_name, 'description': description}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/runtimes',
            headers={'Content-Type': 'application/json'},
            json=RUNTIME_1,
            status_code=201
        )

        ret = self.client.runtimes.create(
            image_name, name=runtime_name, description=description,
            trusted=False
        )

        self.assertEqual(RUNTIME_1, ret.to_dict())
        self.assertEqual(request_data,
                         json.loads(self.requests_mock.last_request.text))

    def test_create_runtime_error(self):
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/runtimes',
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.runtimes.create,
            'image_name'
        )

    def test_delete_runtime(self):
        runtime_id = RUNTIME_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/runtimes/%s' % runtime_id,
            status_code=204
        )
        ret = self.client.runtimes.delete(runtime_id)
        self.assertIsNone(ret)

    def test_delete_runtime_error(self):
        runtime_id = RUNTIME_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/runtimes/%s' % runtime_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=403
        )
        self.assertRaisesRegex(
            exceptions.HTTPForbidden,
            self._error_message,
            self.client.runtimes.delete,
            runtime_id
        )

    def test_get_runtime(self):
        runtime_id = RUNTIME_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/runtimes/%s' % runtime_id,
            headers={'Content-Type': 'application/json'},
            json=RUNTIME_2,
            status_code=200
        )
        ret = self.client.runtimes.get(runtime_id)
        self.assertEqual(RUNTIME_2, ret.to_dict())

    def test_get_runtime_error(self):
        runtime_id = RUNTIME_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/runtimes/%s' % runtime_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.runtimes.get,
            runtime_id
        )

    def test_get_pool_runtime(self):
        runtime_id = RUNTIME_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/runtimes/%s/pool' % runtime_id,
            headers={'Content-Type': 'application/json'},
            json=RUNTIME_POOL,
            status_code=200
        )
        ret = self.client.runtimes.get_pool(runtime_id)
        self.assertEqual(RUNTIME_POOL, ret.to_dict())

    def test_get_pool_runtime_error(self):
        runtime_id = RUNTIME_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/runtimes/%s/pool' % runtime_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.runtimes.get_pool,
            runtime_id
        )
