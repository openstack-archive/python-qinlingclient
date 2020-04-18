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

import copy
import hashlib
from unittest import mock

import six
import uuid

from osc_lib.tests import utils

from qinlingclient.tests.unit import fakes


class FakeQinlingClient(object):

    def __init__(self, **kwargs):
        self.auth_token = kwargs['auth_token']
        self.auth_url = kwargs['auth_url']
        self.runtimes = mock.Mock()
        self.functions = mock.Mock()
        self.function_executions = mock.Mock()
        self.function_versions = mock.Mock()
        self.function_workers = mock.Mock()
        self.jobs = mock.Mock()
        self.webhooks = mock.Mock()
        self.function_aliases = mock.Mock()


class TestQinlingClient(utils.TestCommand):

    def setUp(self):
        super(TestQinlingClient, self).setUp()
        self.app.client_manager.function_engine = FakeQinlingClient(
            auth_token=fakes.AUTH_TOKEN,
            auth_url=fakes.AUTH_URL
        )


class FakeRuntime(object):
    """Fake one or more runtimes."""

    @staticmethod
    def create_one_runtime(attrs=None):
        """Create a fake runtime.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with id, name, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        runtime_attrs = {
            'id': str(uuid.uuid4()),
            'name': 'runtime-name-' + uuid.uuid4().hex,
            'image': 'openstackqinling/python-runtime',
            'status': 'available',
            'description': 'runtime-description-' + uuid.uuid4().hex,
            'is_public': True,
            'trusted': True,
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30'
        }

        # Overwrite default attributes.
        runtime_attrs.update(attrs)

        runtime = fakes.FakeResource(info=copy.deepcopy(runtime_attrs),
                                     loaded=True)

        return runtime

    @staticmethod
    def create_runtimes(attrs=None, count=2):
        """Create multiple fake runtimes.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :param int count:
            The number of runtimes to fake
        :return:
            A list of FakeResource objects faking the runtimes.
        """

        runtimes = []
        for i in range(count):
            runtimes.append(FakeRuntime.create_one_runtime(attrs))

        return runtimes

    @staticmethod
    def get_runtimes(runtimes=None, count=2):
        """Get an iterable Mock object with a list of faked runtimes.

        If runtimes list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List runtimes:
            A list of FakeResource faking runtimes
        :param int count:
            The number of runtimes to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            runtimes.
        """

        if runtimes is None:
            runtimes = FakeRuntime.create_runtimes(count=count)

        return mock.Mock(side_effect=runtimes)

    @staticmethod
    def create_one_runtime_pool(attrs=None):
        """Create a fake runtime pool.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with name, capacity.
        """

        attrs = attrs or {}
        # Set default attributes.
        pool_attrs = {
            'name': 'runtime-id-' + uuid.uuid4().hex,
            'capacity': {'available': 5, 'total': 5}
        }

        # Overwrite default attributes.
        pool_attrs.update(attrs)

        runtime_pool = fakes.FakeResource(info=copy.deepcopy(pool_attrs),
                                          loaded=True)

        return runtime_pool


class FakeFunction(object):
    """Fake one or more functions."""

    @staticmethod
    def get_fake_md5():
        content = uuid.uuid4().hex
        if not isinstance(content, six.binary_type):
            content = content.encode('utf-8')
        return hashlib.md5(content).hexdigest()

    @staticmethod
    def create_one_function(attrs=None):
        """Create a fake function.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with id, name, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        function_attrs = {
            'id': str(uuid.uuid4()),
            'name': 'function-name-' + uuid.uuid4().hex,
            'description': 'function-description-' + uuid.uuid4().hex,
            'count': 0,
            'code': {'md5sum': FakeFunction.get_fake_md5(),
                     'source': 'package'},
            'runtime_id': str(uuid.uuid4()),
            'entry': 'main.main',
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
            'cpu': 100,
            'memory_size': 33554432,
            'timeout': 5
        }

        # Overwrite default attributes.
        function_attrs.update(attrs)

        function = fakes.FakeResource(info=copy.deepcopy(function_attrs),
                                      loaded=True)

        return function

    @staticmethod
    def create_functions(attrs=None, count=2):
        """Create multiple fake functions.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :param int count:
            The number of functions to fake
        :return:
            A list of FakeResource objects faking the functions.
        """

        functions = []
        for i in range(count):
            functions.append(FakeFunction.create_one_function(attrs))

        return functions

    @staticmethod
    def get_functions(functions=None, count=2):
        """Get an iterable Mock object with a list of faked functions.

        If functions list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List functions:
            A list of FakeResource faking functions
        :param int count:
            The number of functions to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            functions.
        """

        if functions is None:
            functions = FakeFunction.create_functions(count=count)

        return mock.Mock(side_effect=functions)


class FakeExecution(object):
    """Fake one or more function executions."""

    @staticmethod
    def create_one_execution(attrs=None):
        """Create a fake function execution.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with id, function_id, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        execution_attrs = {
            'id': str(uuid.uuid4()),
            'function_alias': None,
            'function_id': str(uuid.uuid4()),
            'function_version': 0,
            'description': 'execution-description-' + uuid.uuid4().hex,
            'input': '{"FAKE_INPUT_KEY": "FAKE_INPUT_VALUE"}',
            'result': '{"duration": 1.234, "output": "FAKE_OUTPUT"}',
            'status': 'success',
            'sync': True,
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
        }

        # Overwrite default attributes.
        execution_attrs.update(attrs)

        execution = fakes.FakeResource(info=copy.deepcopy(execution_attrs),
                                       loaded=True)

        return execution

    @staticmethod
    def create_executions(attrs=None, count=2):
        """Create multiple fake function executions.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :param int count:
            The number of function executions to fake
        :return:
            A list of FakeResource objects faking the function executions.
        """

        executions = []
        for i in range(count):
            executions.append(FakeExecution.create_one_execution(attrs))

        return executions

    @staticmethod
    def get_executions(executions=None, count=2):
        """Get an iterable Mock object with a list of faked executions.

        If function executions list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List executions:
            A list of FakeResource faking function executions
        :param int count:
            The number of function executions to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            function executions.
        """

        if executions is None:
            executions = FakeExecution.create_executions(count=count)

        return mock.Mock(side_effect=executions)


class FakeFunctionVersion(object):
    """Fake one or more function versions."""

    @staticmethod
    def create_one_function_version(attrs=None):
        """Create a fake function version.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with id, function_id, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        function_version_attrs = {
            'id': str(uuid.uuid4()),
            'function_id': str(uuid.uuid4()),
            'description': 'function-version-description-' + uuid.uuid4().hex,
            'version_number': 1,
            'count': 0,
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
        }

        # Overwrite default attributes.
        function_version_attrs.update(attrs)

        function_version = fakes.FakeResource(
            info=copy.deepcopy(function_version_attrs),
            loaded=True)

        return function_version

    @staticmethod
    def create_function_versions(attrs=None, count=2):
        """Create multiple fake function versions.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :param int count:
            The number of function versions to fake
        :return:
            A list of FakeResource objects faking the function versions.
        """

        function_versions = []
        for i in range(count):
            function_versions.append(
                FakeFunctionVersion.create_one_function_version(attrs)
            )

        return function_versions

    @staticmethod
    def get_function_versions(function_versions=None, count=2):
        """Get an iterable Mock object with a list of faked function versions.

        If function versions list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List function_versions:
            A list of FakeResource faking function versions
        :param int count:
            The number of function versions to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            function versions.
        """

        if function_versions is None:
            function_versions = FakeFunctionVersion.create_function_versions(
                count=count
            )

        return mock.Mock(side_effect=function_versions)


class FakeFunctionWorker(object):
    """Fake one or more function workers."""

    @staticmethod
    def create_one_function_worker(attrs=None):
        """Create a fake function worker.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :return:
            A FakeResource object, with function_id, worker_name, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        function_worker_attrs = {
            'function_id': str(uuid.uuid4()),
            'worker_name': 'worker-' + uuid.uuid4().hex,
        }

        # Overwrite default attributes.
        function_worker_attrs.update(attrs)

        function_worker = fakes.FakeResource(
            info=copy.deepcopy(function_worker_attrs),
            loaded=True)

        return function_worker

    @staticmethod
    def create_function_workers(attrs=None, count=2):
        """Create multiple fake function workers.

        :param Dictionary attrs:
            A dictionary with all atrributes
        :param int count:
            The number of function workers to fake
        :return:
            A list of FakeResource objects faking the function workers.
        """

        function_workers = []
        for i in range(count):
            function_workers.append(
                FakeFunctionWorker.create_one_function_worker(attrs)
            )

        return function_workers

    @staticmethod
    def get_function_workers(function_workers=None, count=2):
        """Get an iterable Mock object with a list of faked function workers.

        If function workers list is provided, then initialize the Mock
        object with the list. Otherwise create one.

        :param List function_workers:
            A list of FakeResource faking function workers
        :param int count:
            The number of function workers to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            function workers.
        """

        if function_workers is None:
            function_workers = FakeFunctionWorker.create_function_workers(
                count=count
            )

        return mock.Mock(side_effect=function_workers)


class FakeJob(object):
    """Fake one or more jobs."""

    @staticmethod
    def create_one_job(attrs=None):
        """Create a fake job.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, name, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        job_attrs = {
            'id': str(uuid.uuid4()),
            'name': 'job-name-' + uuid.uuid4().hex,
            'count': 3,
            'status': 'RUNNING',
            'function_alias': None,
            'function_id': str(uuid.uuid4()),
            'function_version': 0,
            'function_input': '{"FAKE_INPUT_KEY": "FAKE_INPUT_VALUE"}',
            'pattern': '0 * * * *',  # Once per hour
            'first_execution_time': '2018-08-08T08:00:00',
            'next_execution_time': '2018-08-08T10:00:00',
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
        }

        # Overwrite default attributes.
        job_attrs.update(attrs)

        job = fakes.FakeResource(info=copy.deepcopy(job_attrs), loaded=True)
        return job

    @staticmethod
    def create_jobs(attrs=None, count=2):
        """Create multiple fake jobs.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of jobs to fake
        :return:
            A list of FakeResource objects faking the jobs.
        """

        jobs = []
        for i in range(count):
            jobs.append(FakeJob.create_one_job(attrs))

        return jobs

    @staticmethod
    def get_jobs(jobs=None, count=2):
        """Get an iterable mock object with a list of faked jobs.

        If jobs list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List jobs:
            A list of FakeResource faking jobs
        :param int count:
            The number of jobs to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            jobs.
        """

        if jobs is None:
            jobs = FakeJob.create_jobs(count=count)

        return mock.Mock(side_effect=jobs)


class FakeWebhook(object):
    """Fake one or more webhooks."""

    @staticmethod
    def create_one_webhook(attrs=None):
        """Create a fake webhook.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with id, function_id, etc.
        """

        attrs = attrs or {}
        # Set default attributes.
        webhook_attrs = {
            'id': str(uuid.uuid4()),
            'function_alias': None,
            'function_id': str(uuid.uuid4()),
            'function_version': 0,
            'description': 'webhook-description-' + uuid.uuid4().hex,
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
            'webhook_url': 'http://HOST:PORT/v1/webhooks/FAKE_ID/invoke',
        }

        # Overwrite default attributes.
        webhook_attrs.update(attrs)

        webhook = fakes.FakeResource(info=copy.deepcopy(webhook_attrs),
                                     loaded=True)
        return webhook

    @staticmethod
    def create_webhooks(attrs=None, count=2):
        """Create multiple fake webhooks.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of webhooks to fake
        :return:
            A list of FakeResource objects faking the webhooks.
        """

        webhooks = []
        for i in range(count):
            webhooks.append(FakeWebhook.create_one_webhook(attrs))

        return webhooks

    @staticmethod
    def get_webhooks(webhooks=None, count=2):
        """Get an iterable mock object with a list of faked webhooks.

        If webhooks list is provided, then initialize the Mock object with the
        list. Otherwise create one.

        :param List webhooks:
            A list of FakeResource faking webhooks
        :param int count:
            The number of webhooks to fake
        :return:
            An iterable Mock object with side_effect set to a list of faked
            webhooks.
        """

        if webhooks is None:
            webhooks = FakeWebhook.create_webhooks(count=count)

        return mock.Mock(side_effect=webhooks)


class FakeFunctionAlias(object):
    """Fake one or more function aliases."""

    @staticmethod
    def create_one_function_alias(attrs=None):
        """Create a fake function alias.

        :param Dictionary attrs:
            A dictionary with all attributes
        :return:
            A FakeResource object, with name, function_id, etc.
        """

        attrs = attrs or {}
        # Set default attributes
        function_alias_attrs = {
            'name': 'function-alias-name-' + uuid.uuid4().hex,
            'function_id': str(uuid.uuid4()),
            'description': 'function-alias-description-' + uuid.uuid4().hex,
            'function_version': 0,
            'project_id': str(uuid.uuid4()),
            'created_at': '2018-07-26 09:00:00',
            'updated_at': '2018-07-26 09:00:30',
        }

        # Overwrite default attributes
        function_alias_attrs.update(attrs)

        function_alias = fakes.FakeResource(
            info=copy.deepcopy(function_alias_attrs), loaded=True)
        return function_alias

    @staticmethod
    def create_function_aliases(attrs=None, count=2):
        """Create multiple fake function aliases.

        :param Dictionary attrs:
            A dictionary with all attributes
        :param int count:
            The number of function aliases to fake
        :return:
            A list of FakeResource objects faking the function aliases.
        """

        function_aliases = []
        for i in range(count):
            function_aliases.append(
                FakeFunctionAlias.create_one_function_alias(attrs)
            )

        return function_aliases

    @staticmethod
    def get_function_aliases(function_aliases=None, count=2):
        """Get an iterable mock object with a list of faked function aliases.

        If function aliases list is provided, then initialize the Mock object
        with the list. Otherwise create one.

        :param List function_aliases:
            A list of FakeResource faking function aliases
        :param int count:
            The number of function aliases to fake
        :return
            An iterable Mock object with side_effect set to a list of faked
            function aliases.
        """

        if function_aliases is None:
            function_aliases = FakeFunctionAlias.create_function_aliases(
                count=count
            )

        return mock.Mock(side_effect=function_aliases)
