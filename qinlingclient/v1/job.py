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


class Job(base.Resource):
    pass


class JobManager(base.Manager):
    resource_class = Job

    def list(self, **kwargs):
        return self._list("/v1/jobs", response_key='jobs')

    def create(self, function_alias=None, function_id=None, function_version=0,
               name=None, first_execution_time=None, pattern=None,
               function_input=None, count=None):
        body = {
            "function_alias": function_alias,
            "function_id": function_id,
            "function_version": function_version,
            "name": name,
            "first_execution_time": first_execution_time,
            "pattern": pattern,
            "function_input": function_input,
            "count": count
        }
        return self._create('/v1/jobs', data=body)

    def delete(self, id):
        self._delete('/v1/jobs/%s' % id)

    def get(self, id):
        return self._get('/v1/jobs/%s' % id)

    def update(self, id, **kwargs):
        return self._update('/v1/jobs/%s' % id, kwargs)
