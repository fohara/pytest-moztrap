#!python

import pytest

from connect_results import ConnectResults
from connect_results import InvalidStatusException

class TestResults(object):

    @pytest.mark.parametrize('status', ['passed', 'failed', 'invalidated'])
    def test_valid_status(self, status):
        collector = ConnectResults()
        collector.update("1", "1", status, "comment")

    @pytest.mark.parametrize('status', ['pass', 'fail', 'invalid'])
    def test_invalid_status_throws_exception(self, status):
        collector = ConnectResults()
        e = None
        try:
            collector.update("1", "1", status, "comment")
        except InvalidStatusException as e:
            pass
        assert e.msg == '%s is not a valid status' % status

    def test_failure_can_be_added(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'failed', comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment,
            "bug": None,
            "stepnumber": 0,
        }
        print collector.results
        assert expected in collector.results

    def test_pass_can_be_added(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        collector.update(case_id, env_id, 'passed')

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_can_be_added(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.update(case_id, env_id, 'invalidated', comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "invalidated",
            "comment": comment,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_can_overwrite_pass_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'passed', 'first pass')
        collector.update(case_id, env_id, 'failed', comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": "first pass\n" + comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_can_overwrite_invalid_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'invalidated', "first invalid")
        collector.update(case_id, env_id, 'failed', comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": "first invalid\n" + comment,
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_failure_appends_failure(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'failed', comment)
        collector.update(case_id, env_id, 'failed', "second failure")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment + "\nsecond failure",
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_pass_cannot_overwrite_failure_but_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'failed', comment)
        collector.update(case_id, env_id, 'passed', "first pass")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment + "\nfirst pass",
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_pass_can_overwrite_invalid_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.update(case_id, env_id, 'invalidated', comment)
        collector.update(case_id, env_id, 'passed', "first pass")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
            "comment": comment + "\nfirst pass",
        }
        assert expected in collector._results.values()
        expected.pop('comment')
        assert expected in collector.results
        assert len(collector.results) == 1

    # nobody cares if pass overwrites pass

    def test_invalid_cannot_overwrite_pass_but_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.update(case_id, env_id, 'passed', "first pass")
        collector.update(case_id, env_id, 'invalidated', comment)

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "passed",
            "comment": "first pass\n" + comment,
        }
        assert expected in collector._results.values()
        expected.pop('comment')
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_cannot_overwite_fail_but_appends_comment(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first failure"
        collector.update(case_id, env_id, 'failed', comment)
        collector.update(case_id, env_id, 'invalidated', "first invalid")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "failed",
            "comment": comment + "\nfirst invalid",
            "bug": None,
            "stepnumber": 0,
        }
        assert expected in collector.results
        assert len(collector.results) == 1

    def test_invalid_appends_invalid(self):
        collector = ConnectResults()
        env_id = "1"
        case_id = "1"
        comment = "first invalid"
        collector.update(case_id, env_id, 'invalidated', comment)
        collector.update(case_id, env_id, 'invalidated', "second invalid")

        expected = {
            "environment": env_id, 
            "case": case_id, 
            "status": "invalidated",
            "comment": comment + "\nsecond invalid",
        }
        assert expected in collector.results
        assert len(collector.results) == 1
