# pytest-moztrap

pytest-moztrap is a plugin for [py.test](http://pytest.org/) that
provides integration with Mozilla's MozTrap test case management tool.

**NOTE: This plugin is currently in alpha version and some of the functionality has not been implemented.**

py.test results are translated into MozTrap results using the following lookups:
* failed -> failed
* passed -> passed
* xpassed -> passed
* xfailed -> invalidated
* skipped -> invalidated

In the event that two tests have the same test case id or the test is parameterized, pytest-moztrap aggregates the results and prioritizes failed > passed > invalidated. Details about the multiple results can be found in the comment field (although the MozTrap server does not support the comment field for passing tests so data on xpassing tests may be lost). 

The MozTrap report will be printed if 'T' is included in the -r option. The MozTrap report includes a line for each MozTrap test case with test case id (the id used in the @pytest.mark.moztrap marker), test case run id (for debugging purposes), the MozTrap status of the test, and the test's name in MozTrap. If the --verbose option is used, the contents of the comment field will be printed along with the MozTrap report. One comment line appears for each aggregated result. Parameters used by parametrized tests are included in the comments inside of square brackets, followed by py.test statuses (pass, fail, xpass, xfail, and skipped) and fail reasons, skip reasons, or error message (as applicable).
 

## Continuous Integration

[![Build Status](https://secure.travis-ci.org/davehunt/pytest-moztrap.png?branch=master)](http://travis-ci.org/davehunt/pytest-moztrap)

## Installation

    $ pip install git+https://github.com/klrmn/moztrap-connect/
    $ python setup.py install

## Running

For full usage details run the following command:

    $ py.test --help

    moztrap:
      --mt-url=url        url for the moztrap instance. (default:
                          moztrap.mozilla.org)
      --mt-username=str   moztrap username
      --mt-apikey=str     Ask your MozTrap admin to generate an API key in the
                          Core / ApiKeys table and provide it to you.
      --mt-product=str    product name
      --mt-productversion=str
                          version name
      --mt-run=str        test run name
      --mt-env=str        test environment name
      --mt-coverage       show the coverage report. (default False)

In addition, moztrap reporting can be enabled by including 'T' in the -r option, and additional reporting will be included with the --verbose option.

## Marking tests

To indicate related test cases, use the MozTrap mark as follows:

### Example (single related test case)

    import pytest
    @pytest.mark.moztrap(1000)
    def test_stuff_works():
        assert stuff_works

### Example (multiple related test cases)

    import pytest
    @pytest.mark.moztrap([1001, 1002])
    def test_stuff_works():
        assert stuff_works

## Running the tests for this project

Running the tests has the following required parameters: 
    --test-mt-username
    --test-mt-run
    --test-mt-apikey

The following flags have defaults that can be overwridden: 
    --test-mt-url             (moztrap.allizom.org)
    --test-mt-project         (pytest_moztrap)
    --test-mt-projectversion  (0.1a)
    --test-mt-env             (Android 2.2)

The test_moztrap_report.py and test_moztrap_report_verbose.py files report selected results to moztrap.allizom.org, but the success of this action is not verified within the automation. After running this suite, https://moztrap.allizom.org/results/cases/?filter-run=47 (or adjusted for your current version and run) should show results for all of the test cases, with 3 invalidated, 4 failed, and 8 passing results.
