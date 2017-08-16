from urlparse import urlparse
from itertools import izip_longest


def gen_lines_from_file(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip("\n")
            if line.strip():
                yield line

def _parse_backend_name(line):
    return urlparse(line).netloc if line.startswith('http') else line

def field_map(dictsequence, name, func):
    for d in dictsequence:
        if d[name] is not None:
            d[name] = func(d[name])
        yield d

def gen_lines_to_dictionaries(lines):
    colnames = ('event_time', 'frontend_id', 'event_type', 'replica_group',
                'additional_info')


    log = (dict(izip_longest(colnames, line.rsplit("\t"))) for line in lines)
    log = field_map(log,"event_time", float)
    log = field_map(log,"frontend_id", int)
    log = field_map(log,"replica_group", int)
    log = field_map(log,"additional_info", _parse_backend_name)
    return log

def gen_frontend_ids(log):
    unique_ids = set()
    for item in log:
        if item['frontend_id'] not in unique_ids:
            unique_ids.add(item['frontend_id'])
    return unique_ids

def get_log(filename):
    loglines = gen_lines_from_file(filename)
    return gen_lines_to_dictionaries(loglines)

def gen_filter_by_frontend_id(log, frontend_id):
    return (item for item in log if item['frontend_id'] == frontend_id)

def gen_timestamps_by_frontend_id(log, frontend_id):
    for item in gen_filter_by_frontend_id(log, frontend_id):
        yield int(item['event_time'])
