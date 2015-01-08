#
#  Alcides Viamontes Esquivel
#  Zunzun AB
#  www.zunzun.se
#
#  Copyright 2015
#
#  Distribution of this file is subject
#  to the accompanying licence in this
#  project.
#

"""
Functions for extracting contents from .har files, in particular as Pandas frames...
"""

import json
import datetime as dt
import pandas as pd
import re


def parse_timestamp( ts ) :
    conformant_ts = re.sub(r':(\d\d)$', r'\1', ts)
    return dt.datetime.strptime(conformant_ts,'%Y-%m-%dT%H:%M:%S.%f%z')


def timedelta_to_ms(d):
    return d.seconds * 1000000 + d.microseconds


def datetimediff_to_microseconds( dt1, dt0 ):
    d = dt1 - dt0
    return timedelta_to_ms(d)


def plock(d, keys):
    r = {}
    for k in keys:
        if isinstance(k, str):
            r[k] = d[k]
        else:
            assert isinstance(k, tuple)
            if len(k) == 2:
                (name, transform) = k
                r[name] = transform(d[name])
            elif len(k) == 3:
                (name1, name2, transform) = k
                r[name2] = transform(d[name1])
    return r


def ident(x):
    return x


def headers_size(headers_list):
    return sum( len( header_item['name'] ) + len(header_item['value']) for header_item in headers_list)


def har_to_pandas(f):
    whole_file = json.load( f )
    o1 = whole_file['log']

    # Time of the first request
    page_started_datetime = parse_timestamp(
        o1['pages'][0]['startedDateTime']
    )

    # Although we don't need to use it...
    o2 = o1['entries']
    all_rows = []
    for (i,j_entry) in enumerate(o2):
        row_for_entry= plock( j_entry,
                            [
                                ('startedDateTime', 'started_date_time', parse_timestamp),

                            ]
        )
        row_for_entry.update(plock(j_entry['timings'],
                                   [
                                       ('dns', 'tm_dns', ident),
                                       ('connect', 'tm_connect', ident),
                                       ('blocked', 'tm_blocked', ident),
                                       ('send', 'tm_send', ident),
                                       # ('ssl', 'tm_ssl', ident),
                                       ('receive', 'tm_receive', ident),
                                       ('wait', 'tm_wait', ident),
                                   ]))
        request = j_entry['request']
        response = j_entry['response']
        row_for_entry['sz_request_headers'] = headers_size(request["headers"])
        row_for_entry['sz_response_headers'] = headers_size(response["headers"])
        row_for_entry['sz_request_body'] = len(request.get("content", ''))

        response_content = response.get("content")

        row_for_entry['sz_response_body'] = response_content['size'] if response_content else 0
        row_for_entry['sz_url'] = len(request['url'])

        all_rows.append( row_for_entry)

    frame = pd.DataFrame(all_rows)
    return frame


def main():
    f = open('/home/alcides/projects/AboutSPDY/data/ipython.zunzun.se.har')
    frame = har_to_pandas(f)
    print(frame)


if __name__ == '__main__':
    # Very is-going-not-to-run-at-your-machine test
    main()