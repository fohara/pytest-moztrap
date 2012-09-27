#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest

pytest_plugins = 'pytester'


def pytest_funcarg__testmoztrap(request):
    return TestSetup(request)


def pytest_addoption(parser):
    # required
    group = parser.getgroup('test-moztrap', 'test-moztrap')
    group._addoption('--test-mt-username',
                     action='store',
                     dest='test_moztrap_username',
                     metavar='str',
                     help='moztrap username')
    group._addoption('--test-mt-run',
                     action='store',
                     dest='test_moztrap_run',
                     metavar='str',
                     help='test run name')
    group._addoption('--test-mt-apikey',
                     action='store',
                     dest='test_moztrap_apikey',
                     metavar='str',
                     help='Ask your MozTrap admin to generate an API key in the Core / ApiKeys table and provide it to you.')

    # these have defaults
    group._addoption('--test-mt-url',
                     action='store',
                     dest='test_moztrap_url',
                     default='moztrap.allizom.org',
                     metavar='url',
                     help='url for the moztrap instance. (default for testing: moztrap.allizom.org)')
    group._addoption('--test-mt-product',
                     action='store',
                     dest='test_moztrap_product',
                     default='pytest_moztrap',
                     metavar='str',
                     help='product name')
    group._addoption('--test-mt-productversion',
                     action='store',
                     dest='test_moztrap_product_version',
                     default='0.1a',
                     metavar='str',
                     help='version name')
    group._addoption('--test_mt-env',
                     action='store',
                     dest='test_moztrap_env',
                     default='Android 2.2',
                     metavar='str',
                     help='test environment name')


def pytest_sessionstart(session):
    config = session.config

    if not config.option.test_moztrap_run and \
           config.option.test_moztrap_apikey and \
           config.option.test_moztrap_username:

           raise pytest.UsageError("--test-mt-username, --test-mt-apikey and --test-mt-run are required.")

def pytest_runtest_setup(item):
    TestSetup.username        = item.config.option.test_moztrap_username
    TestSetup.run             = item.config.option.test_moztrap_run
    TestSetup.apikey          = item.config.option.test_moztrap_apikey
    TestSetup.url             = item.config.option.test_moztrap_url
    TestSetup.product         = item.config.option.test_moztrap_product
    TestSetup.product_version = item.config.option.test_moztrap_product_version
    TestSetup.env             = item.config.option.test_moztrap_env


class TestSetup:
    '''
        This class is just used for monkey patching
    '''
    def __init__(self, request):
        self.request = request
