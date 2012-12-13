"""
run "python setup.py develop" before running the contained test
"""
import py
import pytest

@pytest.mark.moztrap(10299)
def test_summary_is_not_output_when_no_id_in_marker(testdir, testmoztrap):
    testdir.makepyfile("""
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
    )
    assert result.ret == 0
    py.test.raises(Exception, result.stdout.fnmatch_lines, ['*MozTrap*'])

@pytest.mark.moztrap(10300)
def test_summary_when_single_id_in_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap(335)
        def test_whatever():
            pass
        """)
    result = testdir.runpytest(
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
        '-r T'
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '335*'])

@pytest.mark.moztrap(10302)
def test_summary_with_xdist_dash_n(testdir, testmoztrap):
    try:
        result = testdir.runpytest('--version')
        result.stderr.fnmatch_lines(['*pytest-xdist*'])
    except Exception:
        import pytest
        pytest.skip("this test requires pytest-xdist")

    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap(336)
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
        '-n 1',
    )
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '336*'])

@pytest.mark.moztrap(10305)
def test_summary_when_multiple_ids_in_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([337, 338])
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
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '337*',
                                 '338*'])

@pytest.mark.moztrap(10307)
def test_duplicate_ids_in_a_single_test_are_removed_from_summary(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([339, 339])
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
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '339*'])
    assert str(result.outlines).count('339') == 1

@pytest.mark.moztrap(10311)
def test_duplicate_ids_across_tests_are_removed_from_summary(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([340])
        def test_whatever1():
            pass
        @pytest.mark.moztrap([340])
        def test_whatever2():
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
    )
    assert result.ret == 0
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '340*'])
    assert str(result.outlines).count('340') == 1

@pytest.mark.moztrap(10312)
def test_duplicate_ids_across_tests_are_removed_from_summary_and_failure_takes_priority(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([341])
        def test_whatever1():
            pass
        @pytest.mark.moztrap([341])
        def test_whatever2():
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
    )
    assert result.ret == 1
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '341* FAILED*'])
    assert str(result.outlines).count('341') == 2

@pytest.mark.moztrap(10313)
def test_duplicate_ids_across_tests_are_removed_from_summary_and_failure_takes_priority_when_final_outcome_is_passed(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([342])
        def test_whatever1():
            assert False
        @pytest.mark.moztrap([342])
        def test_whatever2():
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
    )
    assert result.ret == 1
    result.stdout.fnmatch_lines(['*MozTrap*',
                                 '342* FAILED*'])
    assert str(result.outlines).count('342') == 2

@pytest.mark.moztrap(10314)
def test_summary_does_not_include_ids_not_found_on_moztrap(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([99999999])
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
    )
    assert result.ret == 0
    py.test.raises(Exception, result.stdout.fnmatch_lines, ['*99999999*'])
