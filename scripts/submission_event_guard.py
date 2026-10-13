"""Refuse stale issue results before any reply, result labels or acceptance."""
import json
import sys


def ensure_issue_current(event, current, mode):
    labels = {label['name'] for label in current.get('labels', [])}
    required = {'submission', 'accepted'} if mode == 'accept' else {'submission'}
    if (current.get('state') != 'open' or not required <= labels or mode == 'check' and 'accepted' in labels
            or current.get('body') != event['issue'].get('body')):
        raise ValueError('The issue body, state or review labels changed. These results are stale; no reply or result labels were applied.')


if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as stream: event = json.load(stream)
    with open(sys.argv[2], encoding='utf-8') as stream: current = json.load(stream)
    try:
        ensure_issue_current(event, current, sys.argv[3])
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
