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
        q_list = []
        for key, value in kwargs.items():
            q_list.append('%s=%s' % (key, value))
        q_params = '&'.join(q_list)

        url = '/v1/functions'
        if q_params:
            url += '?%s' % q_params
        return self._list(url, response_key='functions')

    def create(self, code, runtime=None, package=None, **kwargs):
        data = {
            'runtime_id': runtime,
            'code': jsonutils.dumps(code)
        }

        for k, v in kwargs.items():
            if v is not None:
                data.update({k: v})

        params = {"data": data}
        if package:
            params.update({"files": {'package': package}})

        response = self.http_client.request(
            '/v1/functions',
            'POST',
            **params
        )
        body = jsonutils.loads(response.text)

        return self.resource_class(self, body)

    def delete(self, id):
        self._delete('/v1/functions/%s' % id)

    def get(self, id):
        return self._get('/v1/functions/%s' % id)

    def update(self, id, code=None, package=None, **kwargs):
        if code:
            kwargs.update(code)

        params = {"data": kwargs}
        if package:
            params.update({"files": {'package': package}})

        response = self.http_client.request(
            '/v1/functions/%s' % id,
            'PUT',
            **params
        )
        body = jsonutils.loads(response.text)

        return self.resource_class(self, body)

    def detach(self, id):
        return self.http_client.request(
            '/v1/functions/%s/detach' % id,
            'POST',
        )
