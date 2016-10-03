#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pytest
import json

from mtconnect.connect import Connect, ProductVersionDoesNotExistException
from connect_results import ConnectResults

__version__ = '0.1b'


def pytest_addoption(parser):
    group = parser.getgroup('moztrap', 'moztrap')
    group._addoption('--mt-url',
                     action='store',
                     dest='moztrap_url',
                     default='moztrap.mozilla.org',
                     metavar='url',
                     help='url for the moztrap instance. (default: moztrap.mozilla.org)')
    group._addoption('--mt-username',
                     action='store',
                     dest='moztrap_username',
                     metavar='str',
                     help='moztrap username')
    group._addoption('--mt-apikey',
                     action='store',
                     dest='moztrap_apikey',
                     metavar='str',
                     help='Ask your MozTrap admin to generate an API key in the Core / ApiKeys table and provide it to you.')

    group._addoption('--mt-product',
                     action='store',
                     dest='moztrap_product',
                     metavar='str',
                     help='product name')
    group._addoption('--mt-productversion',
                     action='store',
                     dest='moztrap_product_version',
                     metavar='str',
                     help='version name')
    group._addoption('--mt-run',
                     action='store',
                     dest='moztrap_run',
                     metavar='str',
                     help='test run name')

    group._addoption('--mt-env',
                     action='store',
                     dest='moztrap_env',
                     metavar='str',
                     help='test environment name')
    group._addoption('--mt-coverage',
                     action='store_true',
                     default=False,
                     dest='moztrap_coverage',
                     help='show the coverage report. (default False)')

# TODO
#  * consider figuring out the environment based on the WebDriver
#  * fetch and display coverage report for run (this doesn't exist in the API yet)


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'moztrap(*ids): associate MozTrap test cases with the test.')


def pytest_sessionstart(session):
    config = session.config
    # be heavy-handed about making sure we have the data where we need it
    object.__setattr__(config, 'moztrap_run_results', ConnectResults())
    object.__setattr__(config, 'moztrap_test_cases_by_test_case_id', {})
    object.__setattr__(config, 'moztrap_test_cases_by_run_case_id', {})
    object.__setattr__(config, 'moztrap_run_id', None)
    object.__setattr__(config, 'moztrap_env_id', None)
    object.__setattr__(config, 'moztrap_connect_session', None)

    # if any of the auth flags exist
    if config.option.moztrap_username or \
       config.option.moztrap_apikey:

        # then all of them must exist
        if not config.option.moztrap_username or \
           not config.option.moztrap_apikey:

            raise pytest.UsageError(
                "If either of --mt-username or --mt-apikey are specified, both must be specified.")

        # and a session should be opened
        mtsession = Connect(
            'http',
            config.option.moztrap_url,
            config.option.moztrap_username,
            config.option.moztrap_apikey)
            # config.option.moztrap_apikey,
            # DEBUG=True) # having debug on will mess up some of the tests
        config.moztrap_connect_session = mtsession

        # check for moztrap_products, moztrap_version, and moztrap_run
        if not config.option.moztrap_product:
            products = mtsession.get_products()
            product_names = [p['name'] for p in products]
            raise pytest.UsageError(
                "The --mt-product was not specified. Possible projects are:\n%s" %
                "\n".join(product_names))

        if not config.option.moztrap_product_version:
            productversions = mtsession.get_productversions(
                product=config.option.moztrap_product
            )
            version_names = [v['version'] for v in productversions]
            raise pytest.UsageError(
                "The --mt-productversion was not specified. Possible versions are:\n%s" %
                "\n".join(version_names))

        if not config.option.moztrap_run:
            runs = mtsession.get_runs(
                product=config.option.moztrap_product,
                version=config.option.moztrap_product_version
            )
            run_names = [r['name'] for r in runs]
            raise pytest.UsageError(
                "The --mt-run was not specified. Possible (active) runs are:\n%s" %
                "\n".join(run_names))

        # does the run exist?
        runs = []
        try:
            runs = mtsession.get_runs(
                product=config.option.moztrap_product,
                version=config.option.moztrap_product_version,
                name=config.option.moztrap_run,
            )
        except ProductVersionDoesNotExistException:
            pass

        if len(runs) != 1:  # the combination is bad
            productversions = mtsession.get_productversions(
                product=config.option.moztrap_product,
                version=config.option.moztrap_product_version
            )
            if len(productversions) == 1:  # the run is bad
                runs = mtsession.get_runs(
                    product=config.option.moztrap_product,
                    version=config.option.moztrap_product_version
                )
                run_names = [r['name'] for r in runs]
                raise pytest.UsageError(
                    "The --mt-run='%s' was not found. Possible (active) runs are:\n%s" %
                    (config.option.moztrap_run, "\n".join(run_names)))
            else:  # either version or product is bad
                prods = mtsession.get_products(name=config.option.moztrap_product)
                if len(prods) == 1:  # the version is bad
                    productversions = mtsession.get_productversions(
                        product=config.option.moztrap_product,
                    )
                    version_names = [v['version'] for v in productversions]
                    raise pytest.UsageError(
                        "The --mt-productversion='%s' was not found. Possible versions are:\n%s" %
                        (config.option.moztrap_product_version, "\n".join(version_names)))
                else:  # the product is bad
                    products = mtsession.get_products()
                    product_names = [p['name'] for p in products]
                    raise pytest.UsageError("The --mt-product='%s' was not found. Possible products are:\n%s" %
                        (config.option.moztrap_product, "\n".join(product_names)))

        config.moztrap_run_id = runs[0]['id']

        # check for moztrap_env
        environments = mtsession.get_run_environments(config.moztrap_run_id, name=config.option.moztrap_env)
        if len(environments) != 1:
            environments = mtsession.get_run_environments(config.moztrap_run_id)
            env_names = [e['elements'][0]['name'] for e in environments]
            raise pytest.UsageError(
                "The --mt-env was not specified or not found. Possible envs are:\n%s" %
                "\n".join(env_names))
        config.moztrap_env_id = environments[0]['id']

        # lookup table
        run_cases = mtsession.get_run_cases(config.moztrap_run_id, config.moztrap_env_id)
        for case in run_cases:
            case_id = case['caseversion']['case'].split('/')[-2]
            config.moztrap_test_cases_by_test_case_id[case_id] = case


def pytest_terminal_summary(terminalreporter):
    """ adapted from
    https://bitbucket.org/hpk42/pytest/src/a5e7a5fa3c7e/_pytest/skipping.py#cl-179
    """
    tr = terminalreporter
    config = tr.config

    if not tr.reportchars:
        return

    lines = []
    for char in tr.reportchars:
        if char in "T":
            # pull results out of reports and put them into run_results
            for report in get_reports(tr):
                process_report(config, report)

            # figure the output
            show_moztrap(terminalreporter, lines)

    if lines:
        tr._tw.sep("=", "MozTrap test summary info")
        for line in lines:
            tr._tw.line(line)

        report_to_the_mothership(config)
    
def get_reports(tr):
    reports = []
    reports.extend(tr.stats.get("passed", []))
    reports.extend(tr.stats.get("xpassed", []))
    reports.extend(tr.stats.get("failed", []))
    reports.extend(tr.stats.get("skipped", []))
    reports.extend(tr.stats.get("xfailed", []))
    return reports


def process_report(config, report):
    if hasattr(report, 'moztrap_test_case_ids'):
        run_results = config.moztrap_run_results
        for case_id in report.moztrap_test_case_ids:
            if case_id in config.moztrap_test_cases_by_test_case_id.keys():
                status = getattr(report, 'moztrap_status')
                comment = getattr(report, 'moztrap_comment', "")
                run_results.update(case_id, config.moztrap_env_id, status, comment)

def show_moztrap(terminalreporter, lines):
    config = terminalreporter.config
    run_results = config.moztrap_run_results
    verbose = config.option.verbose

    for (key, result) in run_results._results.items():
        case_id = result['case']
        name = config.moztrap_test_cases_by_test_case_id[case_id]['caseversion']['name']
        status = result['status'].upper()
        lines.append("%s %s %s" % (case_id, status, name))
        if verbose > 0:
            comments = result['comment'].split("\n")
            # don't print out lines that just say "\nPASSED"
            if not (len(comments) == 1 and comments[0] == 'PASSED'):
                comments.sort()
                # indent the comments
                lines.append("    %s" % "\n    ".join(comments))


def report_to_the_mothership(config):
    # print 'RESULTS BEING SUBMITTED:\n' + str(config.moztrap_run_results.results)
    if len(config.moztrap_run_results.results):
        mtsession = config.moztrap_connect_session 
        res = mtsession.submit_results(config.moztrap_run_id, config.moztrap_run_results)
        # print "SUBMIT RESULT: " + str(res.text)
        res.raise_for_status()


def pytest_runtest_makereport(__multicall__, item, call):
    report = __multicall__.execute()
    if report.when == 'call' or report.skipped:
        if hasattr(item.obj, 'moztrap'):
            # moztrap case ids
            _marker = getattr(item.obj, 'moztrap')
            _ids = _marker.args[0]
            if not isinstance(_ids, list):
                _ids = [_ids]
            _ids = set(_ids)
            _ids = [unicode(id) for id in _ids]
            object.__setattr__(report, 'moztrap_test_case_ids', _ids)
            _params = ""
            # parameters
            if hasattr(item, 'callspec'):
                if hasattr(item.callspec, 'id'):
                    _params = item.callspec.id
                    if _params:
                        _params = '[' + _params + ']'
                    else:
                        _params = ""

            _reason = ""
            _status = None

            # xfail marker
            if hasattr(item.obj, 'xfail'):
                if report.skipped:
                    _marker = getattr(item.obj, 'xfail')
                    _reason = "XFAILED: " + _marker.kwargs.get('reason', "")
                    _status = 'invalidated'
                elif report.failed:
                    _reason = "XPASSED"
                    _status = 'passed'
                else:
                    print "UNEXPECTED XFAIL SITUATION"
            # in-test xfail reason prior to py.test 2.3
            elif hasattr(report, 'keywords') and 'xfail' in report.keywords.keys():
                _reason = report.keywords.get('xfail', "")
                _reason = "XFAILED: " + _reason.replace('reason: ', "")
                _status = 'invalidated'
            # in-test xfail reason from py.test 2.3 onward
            elif hasattr(report, "wasxfail"):
                _reason = report.wasxfail
                _reason = "XFAILED: " + _reason.replace('reason: ', "")
                _status = 'invalidated'
            # skipped, with reason             
            elif report.skipped:
                _reason = str(report.longrepr[2])
                _reason = _reason.replace('Skipped: ', "SKIPPED: ")
                _status = 'invalidated'
            # failure message
            elif report.failed:
                err_lines = str(report.longrepr).splitlines()
                err_msg = []
                for line in err_lines:
                    if line.startswith('E'):
                        err_msg.append(line)
                _reason = "FAILED: " + "\n".join(err_msg)
                _status = 'failed'
            # passed
            else:
                _reason = "PASSED"
                _status = "passed"

            object.__setattr__(report, 'moztrap_comment', " ".join([_params, _reason]).strip())
            # assert _status
            object.__setattr__(report, 'moztrap_status', _status)

    return report


def pretty_print(dictionary):
    import json
    print json.dumps(dictionary, indent=4)
