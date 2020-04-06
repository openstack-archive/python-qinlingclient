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


class Runtime(base.Resource):
    pass


class RuntimeManager(base.ManagerWithFind):
    resource_class = Runtime

    def list(self, **kwargs):
        return self._list("/v1/runtimes", response_key='runtimes')

    def create(self, image, name=None, description=None,
               is_public=True, trusted=True):
        data = {'image': image, 'is_public': is_public, 'trusted': trusted}
        if name:
            data.update({'name': name})
        if description:
            data.update({'description': description})

        return self._create('/v1/runtimes', data)

    def delete(self, id):
        self._delete('/v1/runtimes/%s' % id)

    def get(self, id):
        return self._get('/v1/runtimes/%s' % id)

    def get_pool(self, id):
        return self._get('/v1/runtimes/%s/pool' % id)
