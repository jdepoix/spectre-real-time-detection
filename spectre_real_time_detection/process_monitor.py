class ProcessMonitor(object):
    def __init__(self):
        self.on_process_start = []
        self.on_process_end = []
        self.running = False

    def process_start(self, pid):
        for callback in self.on_process_start:
            callback(pid)

    def process_end(self, pid):
        for callback in self.on_process_end:
            callback(pid)

    def start(self):
        pass

    def stop(self):
        self.running = False