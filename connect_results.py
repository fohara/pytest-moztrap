#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

class ConnectResults(object):
    """A holder for results of all tests that will be submitted.
    This holder understands the relative importance of the different results.
    """

    def __init__(self):
        self._results = {}
        self.environments = []

    @property
    def results(self):
        results = self._results.values()
        for item in results:
            # add bug and stepnumber fields for failed tests, the API requires them
            if item['status'] == 'failed':
                item['bug'] = None
                item['stepnumber'] = 0
            # remove comment fields from passed tests, API doesn't understand them
            if item['status'] == 'passed':
                item.pop('comment', None)
        return results

    def update(self, case_id, environment_id, new_status, comment=None):
        if not new_status in ('passed', 'failed', 'invalidated'):
            raise InvalidStatusException, "%s is not a valid status" % new_status

        self.environments.append(environment_id)
        key = environment_id + "_" + case_id
        if self._results.has_key(key):
            if comment:
                self.update_comment(key, comment)

            old_status = self._results[key]['status']
            # do not overwrite failed status
            if old_status == 'failed':
                pass
            # overwrite passed and invalidated with failed
            elif new_status == 'failed':
                self.update_status(key, new_status)
            # do not overwrite passed with invalid
            elif old_status == 'passed' and new_status == 'invalid':
                pass
            # overwrite invalid with passed
            elif old_status == 'invalidated' and new_status == 'passed':
                self.update_status(key, new_status)

        else:
            self._results[key] = {
                "environment": environment_id,
                "case": case_id,
                "status": new_status,
                }
            if comment:
                self.update_comment(key, comment)

    def update_comment(self, key, comment):
        if self._results[key].has_key('comment'):
            self._results[key]['comment'] += "\n%s" % comment
        else:
            self._results[key]['comment'] = comment

    def update_status(self, key, status):
        self._results[key]['status'] = status


class InvalidStatusException(Exception):
    def __init__(self, msg):
        self.msg = msg

