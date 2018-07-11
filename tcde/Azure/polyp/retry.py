#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extended HTTP(s) connection classes adding retry for unstable networks
"""

from __future__ import print_function
import sys

from github.Requester import Requester


def __request(self, *args, **kwargs):
    self._retries = 0
    while self._retries < self._max_tries:
        try:
            return super(type(self), self).request(*args, **kwargs)
        except IOError as e:
            ecls = e.__class__
            print('%s.%s: %s (attempt %d of %s)' % (
                ecls.__module__ or '?', ecls.__name__,
                str(e),
                self._retries + 1, self._max_tries),
                file=sys.stderr)
            self.close()
            self._retries += 1
    raise


def retry(cls, times=3):
    assert(times > 0)
    return type('Retry'+cls.__name__, (cls, object), {
        '_max_tries': times,
        '_retries': 0,
        'request': __request,
        })


Requester.injectConnectionClasses(
    retry(Requester._Requester__httpConnectionClass),
    retry(Requester._Requester__httpsConnectionClass))
