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

import uuid

from oslo_serialization import jsonutils

from qinlingclient.common import exceptions
from qinlingclient.tests.unit.v1 import test_client

WEBHOOK_1 = {'id': str(uuid.uuid4()), 'function_id': str(uuid.uuid4())}
WEBHOOK_2 = {'id': str(uuid.uuid4()), 'function_id': str(uuid.uuid4())}

LIST_WEBHOOKS_RESP = {
    'webhooks': [WEBHOOK_1, WEBHOOK_2]
}


class TestWebhook(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_webhook(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/webhooks',
            headers={'Content-Type': 'application/json'},
            json=LIST_WEBHOOKS_RESP,
            status_code=200
        )
        ret = self.client.webhooks.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [WEBHOOK_1, WEBHOOK_2],
            [resource.to_dict() for resource in ret])

    def test_list_webhook_with_params(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/webhooks?function_alias=alias',
            headers={'Content-Type': 'application/json'},
            json=LIST_WEBHOOKS_RESP,
            status_code=200
        )
        ret = self.client.webhooks.list(function_alias='alias')
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [WEBHOOK_1, WEBHOOK_2],
            [resource.to_dict() for resource in ret])

    def test_create_webhook(self):
        function_id = WEBHOOK_1['function_id']
        request_data = {'function_id': function_id, 'function_version': 0}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/webhooks',
            headers={'Content-Type': 'application/json'},
            json=WEBHOOK_1,
            status_code=201
        )
        ret = self.client.webhooks.create(function_id)
        self.assertEqual(WEBHOOK_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_webhook_all_options(self):
        function_id = WEBHOOK_1['function_id']
        function_version = 1
        description = 'A newly created webhook'
        request_data = {'function_id': function_id,
                        'function_version': function_version,
                        'description': description}

        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/webhooks',
            headers={'Content-Type': 'application/json'},
            json=WEBHOOK_1,
            status_code=201
        )
        ret = self.client.webhooks.create(
            function_id, function_version=function_version,
            description=description)
        self.assertEqual(WEBHOOK_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_webhook_error(self):
        function_id = WEBHOOK_1['function_id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/webhooks',
            headers={'Content-Type': 'application/json'},
            text='{"faultstring": "%s"}' % self._error_message,
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.webhooks.create,
            function_id)

    def test_delete_webhook(self):
        webhook_id = WEBHOOK_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            status_code=204
        )
        ret = self.client.webhooks.delete(webhook_id)
        self.assertIsNone(ret)

    def test_delete_webhook_error(self):
        webhook_id = WEBHOOK_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.webhooks.delete,
            webhook_id)

    def test_get_webhook(self):
        webhook_id = WEBHOOK_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            headers={'Content-Type': 'application/json'},
            json=WEBHOOK_2,
            status_code=200
        )
        ret = self.client.webhooks.get(webhook_id)
        self.assertEqual(WEBHOOK_2, ret.to_dict())

    def test_get_webhook_error(self):
        webhook_id = WEBHOOK_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.webhooks.get,
            webhook_id)

    def test_update_webhook(self):
        webhook_id = WEBHOOK_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            headers={'Content-Type': 'application/json'},
            json=WEBHOOK_2,
            status_code=200
        )
        ret = self.client.webhooks.update(webhook_id)
        self.assertEqual(WEBHOOK_2, ret.to_dict())

    def test_update_webhook_with_params(self):
        webhook_id = WEBHOOK_2['id']
        function_id = str(uuid.uuid4())
        description = 'Updated webhook description.'
        request_data = {'function_id': function_id, 'description': description}

        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            headers={'Content-Type': 'application/json'},
            json=WEBHOOK_2,
            status_code=200
        )
        ret = self.client.webhooks.update(webhook_id,
                                          function_id=function_id,
                                          description=description)
        self.assertEqual(WEBHOOK_2, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_update_webhook_error(self):
        webhook_id = WEBHOOK_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/webhooks/%s' % webhook_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.webhooks.update,
            webhook_id)
