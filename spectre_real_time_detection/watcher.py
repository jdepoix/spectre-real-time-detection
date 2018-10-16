from pypapi import papi_low as papi
import time
import os
import numpy as np

from pypapi.exceptions import PapiError

import proc_events


class Watcher(object):
    def __init__(self, events, precision, recv_conn, send_conn):
        self.events = events
        self.precision = precision
        self.recv_conn = recv_conn
        self.send_conn = send_conn
        self.eventsets = {}

    def _attach_process(self, pid):
        if pid not in self.eventsets:
            try:
                eventset = papi.create_eventset()
                papi.add_events(eventset, self.events)
                papi.attach(eventset, pid)
                papi.start(eventset)
                self.eventsets[pid] = eventset
            except PapiError as err:
                #print(err)
                pass

    def _detach_process(self, pid):
        if pid in self.eventsets:
            eventset = self.eventsets[pid]
            papi.stop(eventset)
            papi.cleanup_eventset(eventset)
            papi.destroy_eventset(eventset)
            del self.eventsets[pid]

    def _close(self):
        for eventset in self.eventsets.values():
            papi.stop(eventset)
            papi.cleanup_eventset(eventset)
            papi.destroy_eventset(eventset)

        self.eventsets = {}

    def start(self, processes_to_track):
        values = [0 for _ in self.events]

        papi.library_init()

        own_pid = os.getpid()
        if own_pid in processes_to_track:
            processes_to_track.remove(own_pid)

        for pid in processes_to_track:
            self._attach_process(pid)

        while True:
            pids = []
            readings = []

            for pid, eventset in self.eventsets.items():
                res = papi.accum(eventset, values)
                if res != [0,0,0]:
                    pids.append(pid)
                    readings.append(res)
                # print('{0}: {1}'.format(pid, res))

            if readings:
                self.send_conn.send((pids, np.array(readings)))

            if self.recv_conn.poll():
                event, pid = self.recv_conn.recv()
                if event == proc_events.PROC_START:
                    self._attach_process(pid)
                elif event == proc_events.PROC_END:
                    self._detach_process(pid)
                elif event == proc_events.EXIT:
                    break

            time.sleep(self.precision)

        self._close()
