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

from qinlingclient.tests.unit.v1 import test_client

WORKER_1 = {'function_id': str(uuid.uuid4()), 'worker_name': 'worker_1'}
WORKER_2 = {'function_id': WORKER_1['function_id'], 'worker_name': 'worker_2'}

LIST_FUNCTION_WORKERS_RESP = {
    'workers': [WORKER_1, WORKER_2]
}


class TestFunctionWorker(test_client.TestQinlingClient):

    def test_list_function_worker(self):
        function_id = WORKER_1['function_id']
        self.requests_mock.register_uri(
            'GET',
            test_client.QINLING_URL + '/v1/functions/%s/workers' % function_id,
            headers={'Content-Type': 'application/json'},
            json=LIST_FUNCTION_WORKERS_RESP,
            status_code=200
        )
        ret = self.client.function_workers.list(function_id)
        self.assertIsInstance(ret, list)
        self.assertEqual(
            [WORKER_1, WORKER_2],
            [resource.to_dict() for resource in ret])
