# Copyright 2018 Catalyst IT Limited
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

URL_TEMPLATE = "/v1/functions/%s/versions"


class FunctionVersion(base.Resource):
    pass


class FunctionVersionManager(base.Manager):
    resource_class = FunctionVersion

    def list(self, function_id):
        url = URL_TEMPLATE % function_id
        return self._list(url, response_key='function_versions')

    def create(self, function_id, description=""):
        url = URL_TEMPLATE % function_id
        request_data = {"description": description}

        return self._create(url, data=request_data)

    def delete(self, function_id, version):
        url = URL_TEMPLATE % function_id + '/%s' % version
        self._delete(url)

    def get(self, function_id, version):
        url = URL_TEMPLATE % function_id + '/%s' % version
        return self._get(url)

    def detach(self, function_id, version):
        return self.http_client.request(
            URL_TEMPLATE % function_id + '/%s/detach' % version,
            'POST',
        )
