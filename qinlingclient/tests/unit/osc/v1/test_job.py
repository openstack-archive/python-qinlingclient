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

import datetime
import mock

from osc_lib.tests import utils as osc_tests_utils

from qinlingclient.common import exceptions
from qinlingclient.osc.v1 import base
from qinlingclient.osc.v1 import job
from qinlingclient.tests.unit.osc.v1 import fakes


class TestJob(fakes.TestQinlingClient):

    def setUp(self):
        super(TestJob, self).setUp()
        # Get a shortcut
        self.client = self.app.client_manager.function_engine

        self.columns = base.JOB_COLUMNS
        self.data = []

        self._jobs = fakes.FakeJob.create_jobs(count=3)
        for j in self._jobs:
            self.data.append((j.id, j.name, j.count, j.status,
                              j.function_alias,
                              j.function_id, j.function_version,
                              j.function_input, j.pattern,
                              j.first_execution_time, j.next_execution_time,
                              j.project_id, j.created_at, j.updated_at))


class TestListJob(TestJob):

    def setUp(self):
        super(TestListJob, self).setUp()
        self.cmd = job.List(self.app, None)

        self.columns = [c.capitalize() for c in base.JOB_COLUMNS]

        self.client.jobs.list = mock.Mock(return_value=self._jobs)

    def test_job_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_job_list_with_filter(self):
        arglist = ['--filter', 'name=has:job',
                   '--filter', 'status=eq:running']
        verifylist = [
            ('filters', ['name=has:job', 'status=eq:running']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.list.assert_called_once_with(
            name='has:job', status='eq:running'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_job_list_with_invalid_filter(self):
        arglist = ['--filter', 'name']
        verifylist = [
            ('filters', ['name'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            ValueError,
            '^Invalid filter: name$',
            self.cmd.take_action, parsed_args
        )


class TestCreateJob(TestJob):

    def setUp(self):
        super(TestCreateJob, self).setUp()
        self.cmd = job.Create(self.app, None)

    def _create_fake_job(self, attrs=None):
        # Allow to fake different create results
        j = fakes.FakeJob.create_one_job(attrs)
        self.client.jobs.create = mock.Mock(return_value=j)
        data = (j.id, j.name, j.count, j.status,
                j.function_alias,
                j.function_id, j.function_version,
                j.function_input, j.pattern,
                j.first_execution_time, j.next_execution_time,
                j.project_id, j.created_at, j.updated_at)
        return data

    def test_job_create_function_id(self):
        """Create a job with function id."""
        function_id = self._jobs[0].function_id
        attrs = {'function_id': function_id}
        created_data = self._create_fake_job(attrs)

        arglist = ['--function', function_id]
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('function_alias', None),
            ('name', None),
            ('first_execution_time', None),
            ('pattern', None),
            ('function_input', None),
            ('count', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.create.assert_called_once_with(
            **{'function_alias': None,
               'function_id': function_id, 'function_version': 0,
               'name': None,
               'first_execution_time': None,
               'pattern': None,
               'function_input': None,
               'count': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_job_create_function_name(self):
        """Create a job.

        1. use function name to find the function_id,
        2. all optional params are specified.
        """
        function = fakes.FakeFunction.create_one_function()
        function_name = function.name
        function_id = function.id
        job_name = 'FAKE_JOB_NAME'
        count = 3
        function_version = 1
        function_input = '{"JSON_INPUT_KEY": "JSON_INPUT_VALUE"}'
        pattern = '1 * * * *'
        first_execution_time = str(datetime.datetime.utcnow())
        attrs = {'name': job_name,
                 'count': count,
                 'function_id': function_id,
                 'function_version': function_version,
                 'function_input': function_input,
                 'pattern': pattern,
                 'first_execution_time': first_execution_time}
        created_data = self._create_fake_job(attrs)

        # Use to find the function id with its name
        self.client.functions.find.return_value = function

        arglist = ['--function', function_name,
                   '--function-version', str(function_version),
                   '--name', job_name,
                   '--first-execution-time', first_execution_time,
                   '--pattern', pattern,
                   '--function-input', function_input,
                   '--count', str(count)]
        verifylist = [
            ('function', function_name),
            ('function_version', function_version),
            ('function_alias', None),
            ('name', job_name),
            ('first_execution_time', first_execution_time),
            ('pattern', pattern),
            ('function_input', function_input),
            ('count', count),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.create.assert_called_once_with(
            **{'function_alias': None, 'function_id': function_id,
               'function_version': function_version,
               'name': job_name,
               'first_execution_time': first_execution_time,
               'pattern': pattern,
               'function_input': function_input,
               'count': count}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

        self.client.functions.find.assert_called_once_with(name=function_name)

    def test_job_create_function_alias(self):
        """Create a job with function alias."""
        function_alias = 'fake_alias'
        attrs = {'function_alias': function_alias}
        created_data = self._create_fake_job(attrs)

        arglist = ['--function-alias', function_alias]
        verifylist = [
            ('function', None),
            ('function_version', 0),
            ('function_alias', function_alias),
            ('name', None),
            ('first_execution_time', None),
            ('pattern', None),
            ('function_input', None),
            ('count', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.create.assert_called_once_with(
            **{'function_alias': function_alias,
               'function_id': None, 'function_version': None,
               'name': None,
               'first_execution_time': None,
               'pattern': None,
               'function_input': None,
               'count': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(created_data, data)

    def test_job_create_version_not_integer(self):
        # function_version should be an integer value
        function_id = self._jobs[0].function_id

        arglist = ['--function', function_id, '--function-version',
                   'NOT_A_INTEGER']
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('name', None),
            ('first_execution_time', None),
            ('pattern', None),
            ('function_input', None),
            ('count', None),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_job_create_count_not_integer(self):
        # count should be an integer value
        function_id = self._jobs[0].function_id

        arglist = ['--function', function_id, '--count', 'NOT_A_INTEGER']
        verifylist = [
            ('function', function_id),
            ('function_version', 0),
            ('name', None),
            ('first_execution_time', None),
            ('pattern', None),
            ('function_input', None),
            ('count', 'NOT_A_INTEGER'),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestDeleteJob(TestJob):

    def setUp(self):
        super(TestDeleteJob, self).setUp()
        self.cmd = job.Delete(self.app, None)
        self.client.jobs.delete = mock.Mock(return_value=None)

    def test_job_delete_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_job_delete_one(self):
        job_id = self._jobs[0].id
        arglist = [job_id]
        verifylist = [('job', [job_id])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.client.jobs.delete.assert_called_once_with(job_id)

    def test_job_delete_multiple(self):
        job_ids = [j.id for j in self._jobs]
        arglist = job_ids
        verifylist = [('job', job_ids)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        calls = [mock.call(j_id) for j_id in job_ids]
        self.assertEqual(len(job_ids), self.client.jobs.delete.call_count)
        self.client.jobs.delete.assert_has_calls(calls)

    def test_job_delete_multiple_exception(self):
        job_ids = [j.id for j in self._jobs]
        arglist = job_ids
        verifylist = [('job', job_ids)]

        self.client.jobs.delete = mock.Mock(side_effect=[
            None, RuntimeError, None
        ])

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaisesRegex(
            exceptions.QinlingClientException,
            '^Unable to delete the specified job\(s\)\.$',
            self.cmd.take_action, parsed_args)

        # The second deleteion failed, but the third is done normally
        calls = [mock.call(j_id) for j_id in job_ids]
        self.assertEqual(len(job_ids), self.client.jobs.delete.call_count)
        self.client.jobs.delete.assert_has_calls(calls)


class TestShowJob(TestJob):

    def setUp(self):
        super(TestShowJob, self).setUp()
        self.cmd = job.Show(self.app, None)
        self.client.jobs.get = mock.Mock(return_value=self._jobs[0])

    def test_job_show_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_job_show(self):
        job_id = self._jobs[0].id
        arglist = [job_id]
        verifylist = [('job', job_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.get.assert_called_once_with(job_id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data[0], data)


class TestUpdateJob(TestJob):

    def setUp(self):
        super(TestUpdateJob, self).setUp()
        self.cmd = job.Update(self.app, None)

    def _update_fake_job(self, attrs=None):
        # Allow to fake different update results
        j = fakes.FakeJob.create_one_job(attrs)
        self.client.jobs.update = mock.Mock(return_value=j)
        data = (j.id, j.name, j.count, j.status,
                j.function_alias,
                j.function_id, j.function_version,
                j.function_input, j.pattern,
                j.first_execution_time, j.next_execution_time,
                j.project_id, j.created_at, j.updated_at)
        return data

    def test_job_update_no_option(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_job_update_required_options(self):
        """Update a job.

        Do nothing as only the job_id is specified.
        """
        job_id = self._jobs[0].id
        attrs = {'id': job_id}
        updated_data = self._update_fake_job(attrs)

        arglist = [job_id]
        verifylist = [
            ('id', job_id),
            ('name', None),
            ('status', None),
            ('next_execution_time', None),
            ('pattern', None),
            ('function_input', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.update.assert_called_once_with(
            job_id,
            **{'name': None,
               'status': None,
               'pattern': None,
               'next_execution_time': None,
               'function_input': None}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_job_update_all_options(self):
        job_id = self._jobs[0].id
        name = 'UPDATED_FAKE_JOB_NAME'
        status = 'paused'
        next_execution_time = str(
            datetime.datetime.utcnow() + datetime.timedelta(0, 3600))
        pattern = '* 1 * * *'
        function_input = '{"JSON_INPUT_KEY": "JSON_INPUT_VALUE"}'
        attrs = {'id': job_id, 'name': name, 'status': status,
                 'next_execution_time': next_execution_time,
                 'pattern': pattern, 'function_input': function_input}
        updated_data = self._update_fake_job(attrs)

        arglist = [job_id, '--name', name, '--status', status,
                   '--next-execution-time', next_execution_time,
                   '--pattern', pattern, '--function-input', function_input]
        verifylist = [
            ('id', job_id),
            ('name', name),
            ('status', status),
            ('next_execution_time', next_execution_time),
            ('pattern', pattern),
            ('function_input', function_input),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.client.jobs.update.assert_called_once_with(
            job_id,
            **{'name': name,
               'status': status,
               'pattern': pattern,
               'next_execution_time': next_execution_time,
               'function_input': function_input}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(updated_data, data)

    def test_job_update_status_not_in_choices(self):
        job_id = self._jobs[0].id
        arglist = [job_id, '--status', 'NOT_IN_CHOICES']
        verifylist = [
            ('id', job_id),
            ('name', None),
            ('status', 'NOT_IN_CHOICES'),
            ('next_execution_time', None),
            ('pattern', None),
            ('function_input', None),
        ]

        self.assertRaises(osc_tests_utils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
