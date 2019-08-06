# Copyright 2017 Catalyst IT Limited
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

from qinlingclient.common import base


class FunctionExecution(base.Resource):
    pass


class ExecutionManager(base.Manager):
    resource_class = FunctionExecution

    def list(self, **kwargs):
        q_list = []
        for key, value in kwargs.items():
            q_list.append('%s=%s' % (key, value))
        q_params = '&'.join(q_list)

        url = '/v1/executions'
        if q_params:
            url += '?%s' % q_params
        return self._list(url, response_key='executions')

    def create(self, function_id=None, function_alias=None, function_version=0,
               sync=True, input=None):
        data = {
            'function_id': function_id,
            'function_version': function_version,
            'function_alias': function_alias,
            'sync': sync,
            'input': input
        }
        return self._create('/v1/executions', data)

    def delete(self, id):
        self._delete('/v1/executions/%s' % id)

    def get(self, id):
        return self._get('/v1/executions/%s' % id)

    def get_log(self, id):
        return self._get('/v1/executions/%s/log' % id, return_raw=True)
