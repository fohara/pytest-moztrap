#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
run "python setup.py develop" before running the contained test
"""
import py
import os

from mtconnect.connect import ProductVersionDoesNotExistException


def test_no_exception_if_no_moztrap_flags_specified(testdir):
    file_test = testdir.makepyfile("""
        import pytest
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', '--verbose')
    errmsg = runres.errlines
    assert not errmsg

def test_exception_if_username_exists_and_apikey_does_not(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-username=' + testmoztrap.username)
    errmsg = runres.errlines
    expected = 'ERROR: If either of --mt-username or --mt-apikey are specified, both must be specified.'
    assert expected in errmsg

def test_exception_if_apikey_exists_and_username_does_not(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-apikey=' + testmoztrap.apikey)
    errmsg = runres.errlines
    expected = 'ERROR: If either of --mt-username or --mt-apikey are specified, both must be specified.'
    assert expected in errmsg

def test_no_exception_if_both_username_and_apikey_exist(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
    )
    errmsg = runres.errlines
    expected = 'ERROR: If either of --mt-username or --mt-apikey are specified, both must be specified.'
    assert not expected in errmsg

def test_exception_if_product_not_specified(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-run=' + testmoztrap.run,
    )
    errmsg = runres.errlines
    expected = 'The --mt-product was not specified. Possible projects are:'
    assert expected in errmsg[0]

def test_exception_if_product_version_not_specified(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
    )
    errmsg = runres.errlines
    expected = 'ERROR: The --mt-productversion was not specified. Possible versions are:'
    assert expected in errmsg[0]

def test_exception_if_run_not_specified(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
    )
    errmsg = runres.errlines
    expected = 'ERROR: The --mt-run was not specified. Possible (active) runs are:'
    assert expected in errmsg[0]

def test_exception_when_environment_not_specified(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
    )
    errmsg = runres.errlines
    print errmsg
    expected = "ERROR: The --mt-env was not specified or not found. Possible envs are:"
    assert expected in errmsg[0]
    found = False
    for line in errmsg:
        if line == "Android 2.2":
            found = True
    assert True, "'Android 2.2' not found in %s" % errmsg

def test_product_not_found(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=product will not be found',
        '--mt-run=' + testmoztrap.run,
    )
    errmsg = runres.errlines
    expected = "ERROR: The --mt-product='%s' was not found. Possible products are:" % "product will not be found"
    assert expected in errmsg[0]
    found = False
    for line in errmsg:
        if line == "pytest_moztrap":
            found = True
    assert True, "'pytest_moztrap' not found in %s" % errmsg

def test_product_version_not_found(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=version will not be found',
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
    )
    errmsg = runres.errlines
    expected = "ERROR: The --mt-productversion='%s' was not found. Possible versions are:" % "version will not be found"
    assert expected in errmsg[0]
    found = False
    for line in errmsg:
        if line == "0.1a":
            found = True
    assert True, "'0.1a' not found in %s" % errmsg

def test_run_not_found(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=boogabooga',
    )
    errmsg = runres.errlines
    expected = "ERROR: The --mt-run='%s' was not found. Possible (active) runs are:" % "boogabooga"
    assert expected in errmsg[0]
    found = False
    for line in errmsg:
        if line == "unique name":
            found = True
    assert True, "'unique name' not found in %s" % errmsg

def test_environment_not_found(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=env will not be found',
    )
    errmsg = runres.errlines
    expected = "ERROR: The --mt-env was not specified or not found. Possible envs are:"
    assert expected in errmsg[0]
    found = False
    for line in errmsg:
        if line == "Android 2.2":
            found = True
    assert True, "'Android 2.2' not found in %s" % errmsg

def test_no_error_if_product_version_and_run_all_specified(testdir, testmoztrap):
    file_test = testdir.makepyfile("""
        def test_whatever():
            pass
        """)
    runres = testdir.run('py.test', 
        '--mt-url=' + testmoztrap.url,
        '--mt-username=' + testmoztrap.username, 
        '--mt-apikey=' + testmoztrap.apikey, 
        '--mt-productversion=' + testmoztrap.product_version,
        '--mt-product=' + testmoztrap.product,
        '--mt-run=' + testmoztrap.run,
        '--mt-env=' + testmoztrap.env,
    )
    errmsg = runres.errlines
    assert len(errmsg) == 0


