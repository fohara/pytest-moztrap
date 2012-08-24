__version__ = '0.1a'

test_cases = {}

def pytest_addoption(parser):
    group = parser.getgroup('moztrap', 'moztrap')
    group._addoption('--mt-url',
                     action='store',
                     dest='moztrap_url',
                     default='http://moztrap.mozilla.org',
                     metavar='url',
                     help='url for the moztrap instance')
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
                     help='product identifier')
    # i don't think cycle exists as a moztrap concept
    group._addoption('--mt-cycle',
                     action='store',
                     dest='moztrap_cycle',
                     metavar='str',
                     help='test cycle identifier')
    group._addoption('--mt-run',
                     action='store',
                     dest='moztrap_run',
                     metavar='str',
                     help='test run identifier')
    group._addoption('--mt-suite',
                     action='store',
                     dest='moztrap_suite',
                     metavar='str',
                     help='test suite identifiers (comma separated)')
    group._addoption('--mt-coverage',
                     action='store',
                     dest='moztrap_coverage',
                     metavar='str',
                     help='show the coverage report')

# TODO
#  * import / install mtconnect https://github.com/camd/moztrap-connect
#    http://moztrap-connect.readthedocs.org/en/latest/api.html
#    (git subtree or ask camd to publish to pip?)
#  * connect to moztrap mtconnect.connect.Connect(protocol, host, username, api_key, DEBUG=False)
#  * determine the moztrap env_id relationship to the selenium driver
#  * create a mtconnect.connect.TestResults object
#  * find out if the run specified by --mt-run exists connect.get_runs(**kwargs)
#    * create it if it doesn't exist connect.submit_run(name, description, productversion_id, testresults)
#    * just submit TestResults if it exists connect.submit_results(run_id, testresults)
#  * fetch and display coverage report for run (this doesn't exist in the API yet)
#  @davehunt, please review this before i send the PR to camd
#    * https://github.com/klrmn/moztrap-connect/commit/84d3190995613092167a312467e22f89b5589024

def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'cc(*ids): associate MozTrap test cases with the test.')


def pytest_terminal_summary(terminalreporter):
    config = terminalreporter.config
    if not test_cases or config.option.verbose < 1:
        return
    tw = terminalreporter._tw
    tw.sep('-', 'MozTrap')

    for k, v in test_cases.items():
        #TODO use the MozTrap API to get the description of the test case
        tw.line('%s: %s' % (k, v))


def pytest_runtest_makereport(__multicall__, item, call):
    report = __multicall__.execute()
    if report.when == 'call':
        if hasattr(item.obj, 'moztrap'):
            _marker = getattr(item.obj, 'moztrap')
            _ids = _marker.args[0]
            if not isinstance(_ids, list):
                _ids = [_ids]
            for x in _ids:

                if report.skipped:
                    # TODO: TestResults.addinvalid(case_id, environment_id, comment) ???
                    continue
                if report.failed:
                    # TODO: TestResults.addfail(case_id, environment_id, comment, stepnumber=0, bug=None)
                    # make sure comment has info from parameterize
                    test_cases[x] = report.outcome.upper()
                if report.passed:
                    if not test_cases.has_key(x):
                        # TODO: TestResults.addpass(case_id, environment_id)
                        test_cases[x] = report.outcome.upper()
                # TODO: report xfails and/or xpasses?

    return report
