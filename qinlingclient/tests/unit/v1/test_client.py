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

from keystoneauth1 import session
from requests_mock.contrib import fixture

from osc_lib.tests import utils

from qinlingclient.v1 import client

QINLING_URL = 'http://example.com:7070'


class TestQinlingClient(utils.TestCase):

    def setUp(self):
        super(TestQinlingClient, self).setUp()
        sess = session.Session()
        self.client = client.Client(QINLING_URL, session=sess)
        self.requests_mock = self.useFixture(fixture.Fixture())
