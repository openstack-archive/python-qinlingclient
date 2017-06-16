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

"""OpenStackClient plugin for Function service."""

from osc_lib import utils
from oslo_log import log as logging

from qinlingclient.i18n import _

LOG = logging.getLogger(__name__)

DEFAULT_FUNCTION_ENGINE_API_VERSION = "1"
API_NAME = "function_engine"
API_VERSION_OPTION = "os_function_engine_api_version"
API_VERSIONS = {
    '1': 'qinlingclient.v1.client.Client',
}


def make_client(instance):
    """Returns an qinling service client"""
    function_engine_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)

    LOG.debug("Instantiating function-engine client: {0}".format(
        function_engine_client))

    kwargs = {
        'session': instance.session,
        'service_type': 'function-engine',
        'region_name': instance._region_name
    }

    qinling_endpoint = instance.get_configuration().get('qinling_url')
    if not qinling_endpoint:
        qinling_endpoint = instance.get_endpoint_for_service_type(
            'function-engine',
            region_name=instance._region_name,
            interface=instance._interface
        )

    client = function_engine_client(qinling_endpoint, **kwargs)
    return client


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-function-engine-api-version',
        metavar='<function-engine-api-version>',
        default=utils.env(
            'OS_FUNCTION_ENGINE_API_VERSION',
            default=DEFAULT_FUNCTION_ENGINE_API_VERSION
        ),
        help=_(
            "Function engine API version, default={0}"
            "(Env:OS_FUNCTION_ENGINE_API_VERSION)").format(
            DEFAULT_FUNCTION_ENGINE_API_VERSION
        )
    )
    parser.add_argument('--qinling-url',
                        default=utils.env('QINLING_URL'),
                        help=_('Defaults to env[QINLING_URL].'))
    return parser
