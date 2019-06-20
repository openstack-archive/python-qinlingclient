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

JOB_1 = {'id': str(uuid.uuid4()), 'name': 'job_1',
         'function_id': str(uuid.uuid4())}
JOB_2 = {'id': str(uuid.uuid4()), 'name': 'job_2',
         'function_id': JOB_1['function_id']}

LIST_JOBS_RESP = {
    'jobs': [JOB_1, JOB_2]
}


class TestJob(test_client.TestQinlingClient):

    _error_message = "Test error message."

    def test_list_job(self):
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/jobs',
            headers={'Content-Type': 'application/json'},
            json=LIST_JOBS_RESP,
            status_code=200
        )
        ret = self.client.jobs.list()
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [JOB_1, JOB_2],
            [resource.to_dict() for resource in ret])

    def test_create_job(self):
        function_id = JOB_1['function_id']
        request_data = {'function_id': function_id, 'function_version': 0,
                        'name': None, 'first_execution_time': None,
                        'pattern': None, 'function_input': None,
                        'count': None}
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/jobs',
            headers={'Content-Type': 'application/json'},
            json=JOB_1,
            status_code=201
        )
        ret = self.client.jobs.create(function_id)
        self.assertEqual(JOB_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_job_all_options(self):
        function_id = JOB_1['function_id']
        function_version = 1
        name = JOB_1['name']
        first_execution_time = '2018-08-16T08:00:00'
        pattern = '0 * * * *'
        function_input = '{"name": "Qinling"}'
        count = 3
        request_data = {'function_id': function_id,
                        'function_version': function_version,
                        'name': name,
                        'first_execution_time': first_execution_time,
                        'pattern': pattern, 'function_input': function_input,
                        'count': count}

        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/jobs',
            headers={'Content-Type': 'application/json'},
            json=JOB_1,
            status_code=201
        )
        ret = self.client.jobs.create(
            function_id, function_version=function_version, name=name,
            first_execution_time=first_execution_time, pattern=pattern,
            function_input=function_input, count=count)
        self.assertEqual(JOB_1, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_create_job_error(self):
        function_id = JOB_1['function_id']
        self.requests_mock.register_uri(
            'POST',
            test_client.QINLING_URL + '/v1/jobs',
            headers={'Content-Type': 'application/json'},
            text='{"faultstring": "%s"}' % self._error_message,
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.jobs.create,
            function_id)

    def test_delete_job(self):
        job_id = JOB_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            status_code=204
        )
        ret = self.client.jobs.delete(job_id)
        self.assertIsNone(ret)

    def test_delete_job_error(self):
        job_id = JOB_1['id']
        self.requests_mock.register_uri(
            'DELETE',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.jobs.delete,
            job_id)

    def test_get_job(self):
        job_id = JOB_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            headers={'Content-Type': 'application/json'},
            json=JOB_2,
            status_code=200
        )
        ret = self.client.jobs.get(job_id)
        self.assertEqual(JOB_2, ret.to_dict())

    def test_get_job_error(self):
        job_id = JOB_2['id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=404
        )
        self.assertRaisesRegex(
            exceptions.HTTPNotFound,
            self._error_message,
            self.client.jobs.get,
            job_id)

    def test_update_job(self):
        job_id = JOB_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            headers={'Content-Type': 'application/json'},
            json=JOB_2,
            status_code=200
        )
        ret = self.client.jobs.update(job_id)
        self.assertEqual(JOB_2, ret.to_dict())

    def test_update_job_with_params(self):
        job_id = JOB_2['id']
        name = 'renamed_job'
        pattern = '0 1 * * *'
        request_data = {'name': name, 'pattern': pattern}

        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            headers={'Content-Type': 'application/json'},
            json=JOB_2,
            status_code=200
        )
        ret = self.client.jobs.update(job_id, name=name, pattern=pattern)
        self.assertEqual(JOB_2, ret.to_dict())
        self.assertEqual(jsonutils.dumps(request_data),
                         self.requests_mock.last_request.text)

    def test_update_job_error(self):
        job_id = JOB_2['id']
        self.requests_mock.register_uri(
            'PUT',
            test_client.QINLING_URL + '/v1/jobs/%s' % job_id,
            text='{"faultstring": "%s"}' % self._error_message,
            headers={'Content-Type': 'application/json'},
            status_code=400
        )
        self.assertRaisesRegex(
            exceptions.HTTPBadRequest,
            self._error_message,
            self.client.jobs.update,
            job_id)
