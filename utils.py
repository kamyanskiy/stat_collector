# -*- coding: utf-8 -*-
import io
import heapq
from events import *
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

def get_max_response_time_to_client(total):
    d = dict((k, v["response_time_to_client"]) for k, v in total.items())
    return heapq.nlargest(10, d, key=d.get)
    #return sorted(d, key=d.get, reverse=True)[:10]

def calc_statistic(logname):
    total_stat = {}
    total_stat["frontend_stat"] = {}
    frontend_ids = gen_frontend_ids(get_log(logname))

    for fid in frontend_ids:
        stat = {"start_request": None,
                "backend_connect": [],
                "backend_request": [],
                "backend_ok": [],
                "backend_error": [],
                "start_merge": None,
                "start_send_result": None,
                "finish_request": None,
                "percentile": None,
                "response_time_to_client": None,
                }
        time_sequence = list(gen_timestamps_by_frontend_id(get_log(logname),
                                                           fid))
        stat["percentile"] = int(percentile(time_sequence, .95))
        for ev in gen_filter_by_frontend_id(get_log(logname), fid):
            if ev['event_type'] == 'StartRequest':
                stat['start_request'] = ev['event_time']
            elif ev['event_type'] == 'BackendConnect':
                stat['backend_connect'].append(BackendConnect(
                    event_time=ev['event_time'],
                    additional_info=ev['additional_info'],
                    replica_group=ev['replica_group']
                ))
            elif ev['event_type'] == 'BackendRequest':
                stat['backend_request'].append(BackendRequest(
                    event_time=ev['event_time'],
                    replica_group=ev['replica_group']
                ))
            elif ev['event_type'] == 'BackendOk':
                stat['backend_ok'].append(BackendOk(
                    event_time=ev['event_time'],
                    replica_group=ev['replica_group']
                ))
            elif ev['event_type'] == 'BackendError':
                stat['backend_error'].append(BackendError(
                    event_time=ev['event_time'],
                    additional_info=ev['additional_info'],
                    replica_group=ev['replica_group']
                ))
            elif ev['event_type'] == 'StartMerge':
                stat['start_merge'] = ev['event_time']
            elif ev['event_type'] == 'StartSendResult':
                stat['start_send_result'] = ev['event_time']
            elif ev['event_type'] == 'FinishRequest':
                stat['finish_request'] = ev['event_time']

        stat['response_time_to_client'] = \
            stat['finish_request'] - stat['start_send_result']

        connect_repl_groups = set(
            (i.replica_group for i in stat['backend_connect']))

        ok_repl_groups = set((i.replica_group for i in stat['backend_ok']))

        error_repl_groups = set(
            (i.replica_group for i in stat['backend_error']))

        repl_groups_not_answered = connect_repl_groups - ok_repl_groups

        backend_stat = {}
        errors = {}

        for err_rg in error_repl_groups:
            errors_filtered_by_rg = (
                er for er in stat['backend_error'] if er.replica_group == err_rg)
            errors[err_rg] = {}
            for err_obj in errors_filtered_by_rg:
                if not err_obj.additional_info in errors[err_rg]:
                    errors[err_rg] = {err_obj.additional_info: 1}
                else:
                    errors[err_rg][err_obj.additional_info] += 1

        for rg in connect_repl_groups:
            backend_stat[rg] = {}

            connections_filtered_by_rg = (
                ev for ev in stat['backend_connect'] if ev.replica_group == rg)

            for obj in connections_filtered_by_rg:
                if not obj.additional_info in backend_stat[rg]:
                    backend_stat[rg] = {obj.additional_info: {"access": 1}}
                else:
                    backend_stat[rg][obj.additional_info]["access"] += 1

            backend_stat[rg]["errors"] = errors.get(rg)

        total_stat["frontend_stat"][fid] = {"response_time_to_client": stat[
            "response_time_to_client"],
                           "percentile": stat["percentile"],
                           "groups_not_answered": len(repl_groups_not_answered),
                           "backend_stat": backend_stat,
                           }

        del stat

    total_stat["longest_response_time_to_client_frontend_ids"] = \
            get_max_response_time_to_client(total_stat["frontend_stat"])
    total_stat["logname"] = logname
    return total_stat

def save_report(total_stat, out_filename):
    with io.open(out_filename, "w", encoding="utf-8") as f:
        ten_long_responses = u"10 идентификаторов фронтендов, для которых " \
                             u"фаза отправки запроса была максимальной: {}\n" \
                             u"".format(
                    total_stat["longest_response_time_to_client_frontend_ids"])
        f.write(ten_long_responses)

        for frontend_id in total_stat["frontend_stat"]:
            f.write(u"Идентификатор фронтенда:{} \n".format(frontend_id))

            f.write(u"\tPercentile 95%: {} \n".format(
                total_stat["frontend_stat"][frontend_id]["percentile"])
            )

            f.write(u"\tЗапросов с неполным набором ответивших ГР: {}\n".format(
                total_stat["frontend_stat"][frontend_id]["groups_not_answered"])
            )
            for gr in total_stat["frontend_stat"][frontend_id]["backend_stat"]:
                f.write(u"\tГР: {}\n".format(gr))
                # for backend_info in total_stat["frontend_stat"][frontend_id][
                #     "backend_stat"][gr]:
                backend_info = \
                    total_stat["frontend_stat"][frontend_id]["backend_stat"][gr]
                backend_errors = backend_info.pop('errors')

                for bcnd_name, access in backend_info.items():
                    f.write(u"\t\t {}\n".format(bcnd_name))
                    f.write(u"\t\t\t Кол-во обращений {}\n".format(
                        access['access']))
                    if backend_errors:
                        f.write(u"\t\t\t Ошибки: \n")
                        for k,v in backend_errors.items():
                            f.write(
                                u"\t\t\t\t Тип: {}  Кол-во: {}\n".format(k,v))
                    else:
                        f.write(u"\t\t\t Ошибок нет\n")
