#!/usr/bin/env python3

import os
import socket
import threading
from select import select
from typing import List


class Client:
    def __init__(self, buffer: List) -> None:
        self.stop_pipe_r, self.stop_pipe_w = os.pipe()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.buffer = buffer

    def listen(self):
        self.socket.sendto(b"\x00", ("127.0.0.1", 53000))
        while True:
            readable, _, _ = select([self.socket, self.stop_pipe_r], [], [])
            if self.stop_pipe_r in readable:
                return
            for s in readable:
                data, _ = s.recvfrom(12)
                self.buffer.append(data)

    def shutdown(self):
        # awake blocked select function
        os.write(self.stop_pipe_w, b"\x00")

    def close(self):
        os.close(self.stop_pipe_r)
        os.close(self.stop_pipe_w)
        self.socket.close()


def client_worker(client: Client):
    client.listen()


def main():
    buffer = []
    client = Client(buffer)
    worker = threading.Thread(target=client_worker, args=(client,))
    worker.start()

    while True:
        s = input("> ")
        if s == "q":
            break
        elif s == "ls":
            print("data received:", len(buffer))
            for b in buffer:
                print(b)

    client.shutdown()
    worker.join()
    client.close()

    print("\nbye.")


if __name__ == "__main__":
    main()
