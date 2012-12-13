"""
run "python setup.py develop" before running the contained test
"""
import py
import pytest


@pytest.mark.moztrap(10315)
def test_verbose_report_of_xfail_inside_test(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([343])
        def test_whatever():
            pytest.xfail(reason="it is a bad idea")
            assert False
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '343* INVALIDATED*',
                                 '    XFAILED: it is a bad idea'])

@pytest.mark.moztrap(10316)
def test_verbose_report_of_xfail_test_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([344])
        @pytest.mark.xfail(reason="because we care")
        def test_whatever():
            assert False
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '344* INVALIDATED*',
                                 '    XFAILED: because we care'])

@pytest.mark.moztrap(10317)
def test_verbose_report_of_xpass_test_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([349])
        @pytest.mark.xfail(reason="because we care")
        def test_whatever():
            pass
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '349* PASSED*',
                                 '    XPASSED'])

@pytest.mark.moztrap(10318)
def test_verbose_report_of_xpass_trumps_xfail(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([350])
        @pytest.mark.xfail(reason="because we care")
        @pytest.mark.parametrize('param', [1, 2])
        def test_whatever(param):
            if param == 1:
                assert False
            elif param == 2:
                pass
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '350* PASSED*',
                                 '    [1] XFAILED: because we care',
                                 '    [2] XPASSED'])

# if a test is marked with the @pytest.mark.skipif
# and the condition evaluates to true
# the test case will not show up in the testreporter,
# and therefor will not register a result with
# moztrap

@pytest.mark.moztrap(10319)
def test_verbose_report_of_skipped_test(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([345])
        def test_whatever():
            pytest.skip("it is the wrong thing")
            assert False
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '345* INVALIDATED*',
                                 '    SKIPPED: it is the wrong thing'])

@pytest.mark.moztrap(10320)
def test_verbose_report_of_failed_test(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([346])
        def test_whatever():
            assert False, "explanation"
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 1
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '346* FAILED*',
                                 '*explanation*'])

@pytest.mark.moztrap(10321)
def test_verbose_report_of_parameterized_with_multiple_outcomes(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([347])
        @pytest.mark.parametrize('parameter', [1, 2, 3, 4])
        def test_whatever(parameter):
            if parameter == 1:
                assert True
            elif parameter == 2:
                assert False, 'explanation'
            elif parameter == 3:
                pytest.skip("we do not like threes")
            elif parameter == 4:
                pytest.xfail("four is a four letter word")
                assert False
        """)
    result = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T',
        '--verbose'
    )
    assert result.ret == 1
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '347* FAILED*',
                                 '    [1] PASSED',
                                 '    [2] FAILED: E           AssertionError: explanation',
                                 '    [3] SKIPPED: we do not like threes',
                                 '    [4] XFAILED: four is a four letter word'])
    assert str(result.outlines).count('347') == 2
