#!/usr/bin/env python3

import os
import signal
import socket
import threading
from select import select


class Server:
    def __init__(self, port) -> None:
        self.stop_send = False
        self.stop_event = threading.Event()
        self.stop_pipe_r, self.stop_pipe_w = os.pipe()
        self.client_addr = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("", port))

    def sender(self):
        while not self.stop_send:
            if self.client_addr is not None:
                print("send to", self.client_addr)
                self.socket.sendto(b"hello world\n", self.client_addr)
            self.stop_event.wait(1)

    def serve(self):
        worker = threading.Thread(target=self.sender)
        worker.start()
        while True:
            readable, _, _ = select([self.socket, self.stop_pipe_r], [], [])
            if self.stop_pipe_r in readable:
                return
            for s in readable:
                _, self.client_addr = s.recvfrom(1)
                print("new client", self.client_addr)

    def shutdown(self):
        self.stop_send = True
        self.stop_event.set()
        # awake blocked select function
        os.write(self.stop_pipe_w, b"\x00")

    def close(self):
        os.close(self.stop_pipe_r)
        os.close(self.stop_pipe_w)
        self.socket.close()


def main():
    server = Server(53000)

    def signal_handler(sig, frame):
        server.shutdown()

    signal.signal(signal.SIGINT, signal_handler)

    server.serve()
    server.close()

    print("\nbye.")


if __name__ == "__main__":
    main()
