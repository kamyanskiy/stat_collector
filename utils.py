# -*- coding: utf-8 -*-
import io
import heapq
from events import Event
from generators import *


def percentile(sequence, excelPercentile):
    N = len(sequence)
    n = (N - 1) * excelPercentile + 1
    # Another method: double n = (N + 1) * excelPercentile
    if (n == 1):
        return sequence[0]
    elif (n == N):
        return sequence[N - 1]
    else:
        k = int(n)
        d = n - k
        return sequence[k - 1] + d * (sequence[k] - sequence[k - 1])

def get_call_ids_keys_by_max_values(dictionary):
    # returns 10 keys by 10 largest values
    return heapq.nlargest(10, dictionary, key=dictionary.get)
    #return sorted(d, key=d.get, reverse=True)[:10]

def calc_statistic(logname):
    total_stat = {}
    total_stat['call_stat'] = {}
    total_stat['repl_stat'] = {}

    call_ids = gen_unique_call_ids_list(get_log(logname))

    for call_id in call_ids:

        tmp_stat = {
            'backend_connect': [],
            'backend_request': [],
            'backend_ok': [],
            'backend_error': [],
        }

        for ev in gen_all_events_by_call_id(get_log(logname), call_id):
            if ev['event_type'] == 'StartRequest':
                tmp_stat['start_request'] = ev['timestamp']
            elif ev['event_type'] == 'BackendConnect':
                tmp_stat['backend_connect'].append(Event(**ev))
            elif ev['event_type'] == 'BackendOk':
                tmp_stat['backend_ok'].append(Event(**ev))
            elif ev['event_type'] == 'BackendError':
                tmp_stat['backend_error'].append(Event(**ev))
            elif ev['event_type'] == 'StartMerge':
                tmp_stat['start_merge'] = ev['timestamp']
            elif ev['event_type'] == 'StartSendResult':
                tmp_stat['start_send_result'] = ev['timestamp']
            elif ev['event_type'] == 'FinishRequest':
                tmp_stat['finish_request'] = ev['timestamp']

        # use that to calc 10 longest send to client times
        response_to_client_time = \
            tmp_stat['finish_request'] - tmp_stat['start_send_result']

        # collect that to calc percentile 95
        total_request_time = int(
            tmp_stat['finish_request'] - tmp_stat['start_request'])

        connect_repl_group_set = set(
            (ev.rpl_group for ev in tmp_stat['backend_connect']))

        ok_repl_group_set = set(
            (ev.rpl_group for ev in tmp_stat['backend_ok']))

        repl_groups_not_answered = connect_repl_group_set - ok_repl_group_set

        del tmp_stat

        total_stat['call_stat'][call_id] = {
            "total_request_time": total_request_time,
            "response_to_client_time": response_to_client_time,
            "has_not_answered_groups": len(repl_groups_not_answered) or 0
        }

        for repl_num in connect_repl_group_set:
            total_stat['repl_stat'][repl_num] = {}

        ASK_EVENTS = ['BackendConnect','BackendRequest',
                      'BackendOk', 'BackendError']

        time_line_list = []

        for ev in gen_all_events_by_call_id(get_log(logname), call_id):
            if ev['event_type'] in ASK_EVENTS:
                time_line_list.append(Event(**ev))

        for idx,ev in enumerate(time_line_list):
            if ev.event_type == 'BackendConnect':
                backend = ev.info
                repl = ev.rpl_group
                if not total_stat['repl_stat'][repl]:
                    total_stat['repl_stat'][repl] = {backend: {'errors': {},
                                                                 'access': 1}}

                elif backend not in total_stat['repl_stat'][repl]:
                    total_stat['repl_stat'][repl][backend] = {'errors': {},
                                                                'access': 1}
                elif backend in total_stat['repl_stat'][repl]:
                    total_stat['repl_stat'][repl][backend]['access'] += 1

                for e in time_line_list[idx+1:]:
                    if e.event_type in ('BackendOk', 'BackendError') and e.rpl_group == ev.rpl_group:
                        err = e.info
                        if e.event_type == 'BackendOk':
                            break
                        elif e.event_type == 'BackendError':
                            if not total_stat['repl_stat'][repl][backend]['errors']:
                                total_stat['repl_stat'][repl][backend]['errors'][err] = 1
                            elif err not in total_stat['repl_stat'][repl][backend]['errors']:
                                total_stat['repl_stat'][repl][backend]['errors'][err] = 1
                            elif err in total_stat['repl_stat'][repl][backend]['errors']:
                                total_stat['repl_stat'][repl][backend]['errors'][err] += 1
        # Calc percentile
        rt_sorted = sorted((v["total_request_time"]
                     for k,v in total_stat["call_stat"].items()))

        total_stat["percentile"] = percentile(rt_sorted, .95)

        # Calc 10 long responses
        answ_times = dict((k,int(v['response_to_client_time']))
                      for k,v in total_stat["call_stat"].items())

        total_stat["call_ids_with_long_response_time"] = \
            get_call_ids_keys_by_max_values(answ_times)

        # Calc how much calls which frontend was not receieved answer
        na = sum([v['has_not_answered_groups']
                  for k,v in total_stat['call_stat'].items()])

        total_stat["total_repl_groups_not_annswered"] = na

    return total_stat

def save_report(total_stat, out_filename):
    with io.open(out_filename, "w", encoding="utf-8") as f:
        f.write(u"95й перцентиль времени работы: {} \n\n".format(
            total_stat["percentile"]))

        long_responses = u"Идентификаторы запросов с самой долгой фазой" \
                             u" отправки результатов пользователю: {}\n\n" \
                             u"".format(
                    total_stat["call_ids_with_long_response_time"])
        f.write(long_responses)

        f.write(u"Запросов с неполным набором ответивших ГР: {}\n\n".format(
            total_stat["total_repl_groups_not_annswered"])
        )

        f.write(u"Обращения и ошибки по бекендам: \n")

        for grp in total_stat["repl_stat"]:
            f.write(u"ГР: {}\n".format(grp))
            for backend, info in total_stat["repl_stat"][grp].items():
                f.write(u"\t {}\n".format(backend))

                f.write(u"\t\t Обращений: {}\n".format(info['access']))
                if info['errors']:
                    f.write(u"\t\t Ошибки: \n")
                    for k, v in info['errors'].items():
                        f.write(u"\t\t\t Тип: {}  Кол-во: {}\n".format(k, v))
