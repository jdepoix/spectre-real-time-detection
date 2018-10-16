from multiprocessing import Process, Pipe
from pypapi import events
import psutil

import proc_events
from bcolors import bcolors
from netlink_process_monitor import NetlinkProcessMonitor as ProcessMonitor
from watcher import Watcher
from detector import Detector


def on_process_start(pid):
    watcher_send_conn.send((proc_events.PROC_START, pid))
    print("{0}Start Process {1}".format(bcolors.OKGREEN, pid))


def on_process_end(pid):
    watcher_send_conn.send((proc_events.PROC_END, pid))
    print("{0}End Process {1}".format(bcolors.WARNING, pid))


if __name__ == '__main__':
    events = [events.PAPI_TOT_INS, events.PAPI_L3_TCM, events.PAPI_L3_TCA]

    watcher_recv_conn, watcher_send_conn = Pipe(False)
    detector_recv_conn, detector_send_conn = Pipe(False)
    watcher = Watcher(events, 0.1, watcher_recv_conn, detector_send_conn)
    detector = Detector(detector_recv_conn, None)
    whitelist = []
    running_pids = [x for x in psutil.pids() if x not in whitelist]

    p = Process(target=watcher.start, args=(running_pids,))
    p.start()

    p2 = Process(target=detector.start)
    p2.start()

    process_monitor = ProcessMonitor()
    process_monitor.on_process_start.append(on_process_start)
    process_monitor.on_process_end.append(on_process_end)

    process_monitor.start()
