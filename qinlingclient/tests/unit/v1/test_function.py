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

import six
from six.moves.urllib.parse import urlencode
import uuid

from oslo_serialization import jsonutils

from qinlingclient.common import exceptions
from qinlingclient.tests.unit.v1 import test_client

FUNCTION_1 = {'id': str(uuid.uuid4()), 'name': 'function_1'}
FUNCTION_2 = {'id': str(uuid.uuid4()), 'name': 'function_2'}

LIST_FUNCTIONS_RESP = {
    'functions': [FUNCTION_1, FUNCTION_2]
}


class TestFunction(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_function(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/functions',
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTIONS_RESP,
            status_code=200
        )
        ret = self.client.functions.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [FUNCTION_1, FUNCTION_2],
            [resource.to_dict() for resource in ret])

    def test_list_function_with_params(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/functions?name=test&count=0',
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTIONS_RESP,
            status_code=200
        )
        ret = self.client.functions.list(name='test', count=0)
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [FUNCTION_1, FUNCTION_2],
            [resource.to_dict() for resource in ret])

    def test_create_function(self):
        runtime_id = 'runtime_id'
        code = {'source': 'package', 'md5sum': 'MD5SUM'}
        data = {'runtime_id': runtime_id, 'code': jsonutils.dumps(code)}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/functions',
            headers={'Content-Type': 'application/json'},
            json=FUNCTION_1,
            status_code=201
        )
        ret = self.client.functions.create(code, runtime=runtime_id)
        self.assertEqual(FUNCTION_1, ret.to_dict())
        self.assertEqual(urlencode(data), self.requests_mock.last_request.text)

    def test_create_function_all_options(self):
        runtime_id = 'runtime_id'
        code = {'source': 'package', 'md5sum': 'MD5SUM'}
        package_content = 'package file content'
        package = six.StringIO(package_content)
        cpu = '100'
        memory_size = '33554432'
        data = {'runtime_id': runtime_id, 'code': jsonutils.dumps(code),
                'cpu': cpu, 'memory_size': memory_size}

        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/functions',
            headers={'Content-Type': 'application/json'},
            json=FUNCTION_1,
            status_code=201
        )
        ret = self.client.functions.create(
            code, runtime=runtime_id, package=package,
            cpu=cpu, memory_size=memory_size)
        self.assertEqual(FUNCTION_1, ret.to_dict())

        # Request body is a multipart/form-data
        request_body = self.requests_mock.last_request.body.decode('utf-8')
        param_base_str = ('Content-Disposition: form-data; name="{key}"'
                          '\r\n\r\n{value}')
        file_base_str = ('Content-Disposition: form-data; name="{name}"; '
                         'filename="{filename}"\r\n\r\n{content}')
        for k, v in data.items():
            param_str = param_base_str.format(key=k, value=v)
            self.assertIn(param_str, request_body)
        # filename is same as name since we use a StringIO instead of a
        # real file object in this test.
        file_str = file_base_str.format(name='package', filename='package',
                                        content=package_content)
        self.assertIn(file_str, request_body)

    def test_create_function_error(self):
        runtime_id = 'runtime_id'
        code = {'source': 'package', 'md5sum': 'MD5SUM'}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/functions',
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.functions.create,
            code, runtime=runtime_id)

    def test_delete_function(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            status_code=204
        )
        ret = self.client.functions.delete(function_id)
        self.assertIsNone(ret)

    def test_delete_function_error(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=403
        )
        self.assertRaisesRegex(
            exceptions.HTTPForbidden,
            self._error_message,
            self.client.functions.delete,
            function_id
        )

    def test_get_function(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            headers={'Content-Type': 'application/json'},
            json=FUNCTION_2,
            status_code=200
        )
        ret = self.client.functions.get(function_id)
        self.assertEqual(FUNCTION_2, ret.to_dict())
        self.assertFalse(self.requests_mock.last_request.stream)

    def test_get_function_download(self):
        function_id = FUNCTION_2['id']
        function_data = 'function package data'
        self.requests_mock.register_uri(
            'GET',
            (test_client.QINLING_URL +
             '/v1/functions/%s?download=true' % function_id),
            headers={'Content-Type': 'application/zip'},
            text=function_data,
            status_code=200
        )
        ret = self.client.functions.get(function_id, download=True)
        self.assertEqual(function_data, ret.text)
        self.assertEqual('application/zip', ret.headers['content-type'])
        self.assertTrue(self.requests_mock.last_request.stream)

    def test_get_function_error(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.functions.get,
            function_id
        )

    def test_update_function(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            headers={'Content-Type': 'application/json'},
            json=FUNCTION_2,
            status_code=200
        )
        ret = self.client.functions.update(function_id)
        self.assertEqual(FUNCTION_2, ret.to_dict())

    def test_update_function_all_options(self):
        function_id = FUNCTION_2['id']
        code = {'source': 'package'}
        package_content = 'updated package file content'
        package = six.StringIO(package_content)
        cpu = '100'
        memory_size = '33554432'
        data = {'source': 'package', 'cpu': cpu, 'memory_size': memory_size}

        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            headers={'Content-Type': 'application/json'},
            json=FUNCTION_2,
            status_code=200
        )
        ret = self.client.functions.update(
            function_id, code=code, package=package,
            cpu=cpu, memory_size=memory_size)
        self.assertEqual(FUNCTION_2, ret.to_dict())

        # Request body is a multipart/form-data
        request_body = self.requests_mock.last_request.body.decode('utf-8')
        param_base_str = ('Content-Disposition: form-data; name="{key}"'
                          '\r\n\r\n{value}')
        file_base_str = ('Content-Disposition: form-data; name="{name}"; '
                         'filename="{filename}"\r\n\r\n{content}')
        for k, v in data.items():
            param_str = param_base_str.format(key=k, value=v)
            self.assertIn(param_str, request_body)
        # filename is same as name since we use a StringIO instead of a
        # real file object in this test.
        file_str = file_base_str.format(name='package', filename='package',
                                        content=package_content)
        self.assertIn(file_str, request_body)

    def test_update_function_error(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/functions/%s' % function_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=403
        )
        self.assertRaisesRegex(
            exceptions.HTTPForbidden,
            self._error_message,
            self.client.functions.update,
            function_id)

    def test_detach_function(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/functions/%s/detach' % function_id,
            status_code=202
        )
        ret = self.client.functions.detach(function_id)
        self.assertEqual('', ret.text)
        self.assertEqual(202, ret.status_code)

    def test_detach_function_error(self):
        function_id = FUNCTION_2['id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/functions/%s/detach' % function_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.functions.detach,
            function_id)

    def test_scaleup_function(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'POST',
            (test_client.QINLING_URL +
             '/v1/functions/%s/scale_up' % function_id),
            status_code=202
        )
        resp, text = self.client.functions.scaleup(function_id)
        self.assertEqual('', text)
        self.assertEqual(202, resp.status_code)
        self.assertEqual(jsonutils.dumps({'count': 1}),
                         self.requests_mock.last_request.text)

    def test_scaleup_function_error(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'POST',
            (test_client.QINLING_URL +
             '/v1/functions/%s/scale_up' % function_id),
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.functions.scaleup,
            function_id)

    def test_scaledown_function(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'POST',
            (test_client.QINLING_URL +
             '/v1/functions/%s/scale_down' % function_id),
            status_code=202
        )
        resp, text = self.client.functions.scaledown(function_id, count=2)
        self.assertEqual('', text)
        self.assertEqual(202, resp.status_code)
        self.assertEqual(jsonutils.dumps({'count': 2}),
                         self.requests_mock.last_request.text)

    def test_scaledown_function_error(self):
        function_id = FUNCTION_1['id']
        self.requests_mock.register_uri(
            'POST',
            (test_client.QINLING_URL +
             '/v1/functions/%s/scale_down' % function_id),
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.functions.scaledown,
            function_id)
