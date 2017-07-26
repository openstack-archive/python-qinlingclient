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

from oslo_serialization import jsonutils

from qinlingclient.common import base


class Function(base.Resource):
    pass


class FunctionManager(base.Manager):
    resource_class = Function

    def list(self, **kwargs):
        return self._list("/v1/functions", response_key='functions')

    def create(self, name, runtime, code, package, entry=None):
        data = {
            'name': name,
            'runtime_id': runtime,
            'code': jsonutils.dumps(code)
        }
        if entry:
            data['entry'] = entry

        response = self.http_client.request(
            '/v1/functions',
            'POST',
            data=data,
            files={'package': package}
        )
        body = jsonutils.loads(response.text)

        return self.resource_class(self, body)

    def delete(self, id):
        self._delete('/v1/functions/%s' % id)

    def get(self, id):
        return self._get('/v1/functions/%s' % id)
