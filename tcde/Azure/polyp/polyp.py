#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Merge the default (usually ``master``) branch into topic branches.

USAGE: ./polyp.py repository
""" 

import sys

# argument parser
import argparse
argparser = argparse.ArgumentParser(description='Merge the default (usually master) branch into topic branches')
argparser.add_argument('repository', help='the repository in which to merge')
argparser.add_argument('commitish', help='the commit to merge from instead of the tip of the default branch', nargs='?', default=None)
argparser.add_argument('-t', '--oauth', help='OAuth2 token')
argparser.add_argument('-u', '--user', help='github username')
argparser.add_argument('-n', '--dry-run', help='print what would be done but don\'t perform actual merge', action='store_true')
argparser.add_argument('-q', '--quiet', help='be quiet', action='store_true')
argparser.add_argument('-v', '--verbose', help='be verbose', action='store_true')
argparser.add_argument('--timeout', help='operation timeout in seconds', type=int, default=60)
argparser.add_argument('--trace', help='trace github API calls', action='store_true')
__doc__ = argparser.format_help()


# debug output
def verbose(msg, *fmtargs):
    if args.verbose:
        print msg % fmtargs
def info(msg, *fmtargs):
    if not args.quiet:
        print msg % fmtargs

from github import Github, GithubException
import retry


def get_filters(repo):
    """filters for determining which branches to merge to"""
    cache = {}
    def compare(a, b):
        """Perform comparison between two brances or commitishes"""
        try:
            (ca, cb, cc) = cache['last_compare']
            if a == ca and b == cb:
                return cc
        except (KeyError, IndexError):
            pass
        c = repo.compare(
            isinstance(a, basestring) and a or a.name,
            isinstance(b, basestring) and b or b.name)
        cache['last_compare'] = (a, b, c)
        return c

    def bugs(branches):
        """Add the bugs branch to the list"""
        yield repo.get_branch('bugs')
        for branch in branches:
            yield branch

    def topics(branches):
        """Filter for topic branches by name"""
        for branch in branches:
            if (branch.name.startswith('topic-') or
                branch.name.startswith('bugfix-')):
                yield branch

    def diverged(branches):
        """Filter for topics that have diverged from the reference commit"""
        for branch in branches:
            if compare(args.commitish, branch).status == 'diverged':
                yield branch

    def recent(branches):
        """Filter out branches that haven't been touched in a long time"""
        from datetime import datetime, timedelta
        earliest = datetime(2014,1,1)
        now = datetime.utcnow()
        delta = timedelta(180)
        for branch in branches:
            dt = branch.commit.commit.committer.date
            if dt > earliest and now - dt < delta:
                yield branch

    def nonrelease(branches):
        """Filter out branches that are from release branches, not trunk"""
        def get_merge_base(b):
            """find the merge base commit between b and the reference commitish"""
            try:
                return compare(args.commitish, b).merge_base_commit
            except GithubException as e:
                if not (e.data and e.data[u'message'] and e.data[u'message'].find(u'diff is taking too long') >= 0):
                    raise
                else:
                    verbose('compare took too long for %s', b.name)

        for branch in branches:
            # bugs is never from a release branch
            if branch.name == 'bugs':
                yield branch
                continue

            if not cache.has_key('release_branches'):
                cache['release_branches'] = [(b, get_merge_base(b)) for b in repo.get_branches() if b.name.startswith('release-')]

            m = get_merge_base(branch)
            if m is None:
                continue

            for r, base in cache['release_branches']:
                if base is None:
                    continue
                elif m == base:
                    verbose('%s branched from %s', branch.name, r.name)
                    break
            else:
                yield branch

    def closed(branches):
        """Filter out branches that have a .closed lightweight tag"""
        for branch in branches:
            tagname = branch.name + '.closed'
            try:
                tag = repo.get_git_ref('tags/'+tagname)
                verbose('%s is closed at %s', branch.name, tag.object.sha)
                if branch.commit.sha != tag.object.sha:
                    verbose('%s does not point to the tip of %s', tagname, branch.name)
            except GithubException as e:
                if e.status == 404:
                    yield branch
                else:
                    raise

    return [
        topics,
        closed,
        recent,
        # bugs,
        diverged,
        nonrelease,
    ]

def connect(repo):
    if args.oauth:
        gh = Github(args.oauth, timeout=args.timeout)
    else:
        from getpass import getpass, getuser
        gh = Github(args.user or getuser(), getpass(), timeout=args.timeout)
    return gh.get_repo(repo)

if __name__ == '__main__':
    global args
    args = argparser.parse_args()
    if args.trace:
        from github import Requester
        import logging
        tracer = logging.getLogger(Requester.__name__)
        tracer.addHandler(logging.StreamHandler(sys.stdout))
        tracer.setLevel(logging.DEBUG)
    repo = connect(args.repository)
    verbose('Connected to %s', repo.name)
    if not args.commitish:
        args.commitish = repo.default_branch
    verbose('merging from %s', args.commitish)

    conflicts = 0
    for b in reduce(lambda x, y: y(x), get_filters(repo), repo.get_branches()):
        (args.dry_run and info or verbose)('merging %s to %s', args.commitish, b.name)
        if args.dry_run:
            continue
        try:
            c = repo.merge(b.name, args.commitish)
            info('%s', c.commit.message)
        except GithubException as e:
            if e.status == 409:
                info('Could not merge %s into %s: %s (%s)', args.commitish, b.name, e.data['message'], b.commit.author.name)
                conflicts = conflicts + 1
            else:
                raise
    sys.exit(conflicts and 1 or 0)

