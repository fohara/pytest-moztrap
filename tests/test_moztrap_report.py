"""
run "python setup.py develop" before running the contained test
"""
import py

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

def test_summary_when_single_id_in_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap(730)
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
                                 '730*'])

def test_summary_with_xdist_dash_n(testdir, testmoztrap):
    try:
        result = testdir.runpytest('--version')
        result.stderr.fnmatch_lines(['*pytest-xdist*'])
    except Exception:
        import pytest
        pytest.skip("this test requires pytest-xdist")

    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap(731)
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
                                 '731*'])

def test_summary_when_multiple_ids_in_marker(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([732, 733])
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
                                 '732*',
                                 '733*'])

def test_duplicate_ids_in_a_single_test_are_removed_from_summary(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([734, 734])
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
                                 '734*'])
    assert str(result.outlines).count('734/') == 1

def test_duplicate_ids_across_tests_are_removed_from_summary(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([735])
        def test_whatever1():
            pass
        @pytest.mark.moztrap([735])
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
                                 '735*'])
    assert str(result.outlines).count('735/') == 1

def test_duplicate_ids_across_tests_are_removed_from_summary_and_failure_takes_priority(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([736])
        def test_whatever1():
            pass
        @pytest.mark.moztrap([736])
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
                                 '736/* FAILED*'])
    assert str(result.outlines).count('736/') == 1

def test_duplicate_ids_across_tests_are_removed_from_summary_and_failure_takes_priority_when_final_outcome_is_passed(testdir, testmoztrap):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.moztrap([737])
        def test_whatever1():
            assert False
        @pytest.mark.moztrap([737])
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
                                 '737/* FAILED*'])
    assert str(result.outlines).count('737/') == 1

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
