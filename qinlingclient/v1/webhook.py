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


class Webhook(base.Resource):
    pass


class WebhookManager(base.Manager):
    resource_class = Webhook

    def list(self, **kwargs):
        q_list = []
        for key, value in kwargs.items():
            q_list.append('%s=%s' % (key, value))
        q_params = '&'.join(q_list)

        url = '/v1/webhooks'
        if q_params:
            url += '?%s' % q_params
        return self._list(url, response_key='webhooks')

    def create(self, function_id, function_alias=None, function_version=0,
               description=None):
        data = {
            'function_id': function_id,
            'function_version': function_version,
            'function_alias': function_alias
        }
        if description:
            data.update({'description': description})

        return self._create('/v1/webhooks', data)

    def delete(self, id):
        self._delete('/v1/webhooks/%s' % id)

    def get(self, id):
        return self._get('/v1/webhooks/%s' % id)

    def update(self, id, **kwargs):
        """Update webhook.

        function_id, function_version and description are supported.
        """
        body = {}
        for k, v in kwargs.items():
            if v is not None:
                body.update({k: v})

        return self._update('/v1/webhooks/%s' % id, kwargs)
