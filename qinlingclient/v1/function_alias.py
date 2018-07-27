# Copyright 2018 OpenStack Foundation.
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

URL_TEMPLATE = "/v1/aliases"


class FunctionAlias(base.Resource):
    pass


class FunctionAliasManager(base.Manager):
    resource_class = FunctionAlias

    def list(self, **kwargs):
        url = URL_TEMPLATE
        return self._list(url, response_key='function_aliases')

    def create(self, name, function_id, function_version=0, description=""):
        url = URL_TEMPLATE
        request_data = {
            'name': name,
            'function_id': function_id,
            'function_version': function_version,
            'description': description
        }

        return self._create(url, data=request_data)

    def delete(self, name):
        url = URL_TEMPLATE + '/%s' % name
        self._delete(url)

    def get(self, name):
        url = URL_TEMPLATE + '/%s' % name
        return self._get(url)

    def update(self, name, function_id=None, function_version=None,
               description=None):
        url = URL_TEMPLATE + '/%s' % name
        request_data = {
            'function_id': function_id,
            'function_version': function_version,
            'description': description
        }

        return self._update(url, data=request_data)
