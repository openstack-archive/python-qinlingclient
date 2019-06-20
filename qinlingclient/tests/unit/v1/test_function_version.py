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

VERSION_1 = {'id': str(uuid.uuid4()), 'function_id': str(uuid.uuid4()),
             'version_number': 1}
VERSION_2 = {'id': str(uuid.uuid4()), 'function_id': VERSION_1['function_id'],
             'version_number': 2}

LIST_FUNCTION_VERSIONS_RESP = {
    'function_versions': [VERSION_1, VERSION_2]
}

URL_TEMPLATE = "/v1/functions/%s/versions"


class TestFunctionVersion(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_function_version(self):
        function_id = VERSION_1['function_id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + URL_TEMPLATE % function_id,
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTION_VERSIONS_RESP,
            status_code=200
        )
        ret = self.client.function_versions.list(function_id)
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [VERSION_1, VERSION_2],
            [resource.to_dict() for resource in ret])

    def test_create_function_version(self):
        function_id = VERSION_1['function_id']
        request_data = {'description': ''}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + URL_TEMPLATE % function_id,
            headers={'Content-Type': 'application/json'},
            json=VERSION_1,
            status_code=201
        )
        ret = self.client.function_versions.create(function_id)
        self.assertEqual(VERSION_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_version_all_options(self):
        function_id = VERSION_1['function_id']
        description = 'This a newly created function version.'
        request_data = {'description': description}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + URL_TEMPLATE % function_id,
            headers={'Content-Type': 'application/json'},
            json=VERSION_1,
            status_code=201
        )
        ret = self.client.function_versions.create(
            function_id, description=description)
        self.assertEqual(VERSION_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_function_version_error(self):
        function_id = VERSION_1['function_id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + URL_TEMPLATE % function_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=500
        )
        self.assertRaisesRegex(
            exceptions.HTTPInternalServerError,
            self._error_message,
            self.client.function_versions.create,
            function_id)

    def test_delete_function_version(self):
        function_id = VERSION_1['function_id']
        version = VERSION_1['version_number']
        url = URL_TEMPLATE % function_id + '/%s' % version
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + url,
            status_code=204
        )
        ret = self.client.function_versions.delete(function_id, version)
        self.assertIsNone(ret)

    def test_delete_function_version_error(self):
        function_id = VERSION_1['function_id']
        version = VERSION_1['version_number']
        url = URL_TEMPLATE % function_id + '/%s' % version
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + url,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=403
        )
        self.assertRaisesRegex(
            exceptions.HTTPForbidden,
            self._error_message,
            self.client.function_versions.delete,
            function_id, version
        )

    def test_get_function_version(self):
        function_id = VERSION_2['function_id']
        version = VERSION_2['version_number']
        url = URL_TEMPLATE % function_id + '/%s' % version
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + url,
            headers={'Content-Type': 'application/json'},
            json=VERSION_2,
            status_code=200
        )
        ret = self.client.function_versions.get(function_id, version)
        self.assertEqual(VERSION_2, ret.to_dict())

    def test_get_function_version_error(self):
        function_id = VERSION_2['function_id']
        version = VERSION_2['version_number']
        url = URL_TEMPLATE % function_id + '/%s' % version
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + url,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_versions.get,
            function_id, version
        )

    def test_detach_function_version(self):
        function_id = VERSION_2['function_id']
        version = VERSION_2['version_number']
        url = URL_TEMPLATE % function_id + '/%s/detach' % version
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + url,
            status_code=202
        )
        ret = self.client.function_versions.detach(function_id, version)
        self.assertEqual('', ret.text)
        self.assertEqual(202, ret.status_code)

    def test_detach_function_version_error(self):
        function_id = VERSION_2['function_id']
        version = VERSION_2['version_number']
        url = URL_TEMPLATE % function_id + '/%s/detach' % version
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + url,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.function_versions.detach,
            function_id, version
        )
