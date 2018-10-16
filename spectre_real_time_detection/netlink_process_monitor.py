import os
import socket
import struct

from process_monitor import ProcessMonitor

if getattr(socket, "NETLINK_CONNECTOR", None) is None:
    socket.NETLINK_CONNECTOR = 11

CN_IDX_PROC = 1
CN_VAL_PROC = 1

NLMSG_NOOP = 1
NLMSG_ERROR = 2
NLMSG_DONE = 3
NLMSG_OVERRUN = 4

PROC_CN_MCAST_LISTEN = 1
PROC_CN_MCAST_IGNORE = 2

PROC_EVENT_NONE = 0
PROC_EVENT_FORK = 1
PROC_EVENT_EXIT = 0x80000000


class NetlinkProcessMonitor(ProcessMonitor):
    def __init__(self):
        super().__init__()

    def start(self):
        # FIXME: Hardcoded structs are not portable
        import platform
        assert platform.processor() == "x86_64"

        # Create Netlink socket
        sock = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM,
                             socket.NETLINK_CONNECTOR)
        sock.bind((os.getpid(), CN_IDX_PROC))

        # Send PROC_CN_MCAST_LISTEN
        data = struct.pack("=IHHII IIIIHH I",
                           16 + 20 + 4, NLMSG_DONE, 0, 0, os.getpid(),
                           CN_IDX_PROC, CN_VAL_PROC, 0, 0, 4, 0,
                           PROC_CN_MCAST_LISTEN)
        if sock.send(data) != len(data):
            raise RuntimeError("Failed to send PROC_CN_MCAST_LISTEN")

        self.running = True

        while self.running:
            data, (nlpid, nlgrps) = sock.recvfrom(1024)

            # Netlink message header (struct nlmsghdr)
            msg_len, msg_type, msg_flags, msg_seq, msg_pid \
                = struct.unpack("=IHHII", data[:16])
            data = data[16:]

            if msg_type == NLMSG_NOOP:
                continue
            if msg_type in (NLMSG_ERROR, NLMSG_OVERRUN):
                break

            data = data[20:]

            # Process event message (struct proc_event)
            what, cpu, timestamp = struct.unpack("=LLQ", data[:16])
            data = data[16:]
            if what == PROC_EVENT_NONE:
                continue

            if what == PROC_EVENT_FORK:
                parent_pid, parent_tgid, child_pid, child_tgid = struct.unpack("=IIII", data[:16])

                if child_pid == child_tgid:  # Process and not thread started
                    self.process_start(child_pid)
            elif what == PROC_EVENT_EXIT:
                pid, tgid = struct.unpack("=II", data[:8])

                if pid == tgid:  # Process and not thread stopped
                    self.process_end(pid)

        sock.close()
