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

def gen_lines_to_dicts(lines):
    colnames = ('timestamp', 'call_id', 'event_type', 'rpl_group', 'info')
    log = (dict(izip_longest(colnames, line.rsplit("\t"))) for line in lines)
    log = field_map(log,"timestamp", float)
    log = field_map(log,"call_id", int)
    log = field_map(log,"rpl_group", int)
    log = field_map(log,"info", _parse_backend_name)
    return log

def gen_unique_call_ids_list(log):
    unique_ids = set()
    for item in log:
        if item['call_id'] not in unique_ids:
            unique_ids.add(item['call_id'])
    return unique_ids

def get_log(filename):
    return gen_lines_to_dicts(gen_lines_from_file(filename))

def gen_all_events_by_call_id(log, call_id):
    return (item for item in log if item['call_id'] == call_id)

def gen_timestamps_by_call_id(log, call_id):
    for item in gen_all_events_by_call_id(log, call_id):
        yield int(item['call_id'])
