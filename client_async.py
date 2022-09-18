#!/usr/bin/env python3

import asyncio
import sys


class ClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, buffer) -> None:
        super().__init__()
        self.client_addr = None
        self.stop = False
        self.buffer = buffer

    def connection_made(self, transport):
        self.transport = transport
        self.transport.sendto(b"\x00")

    def datagram_received(self, data, addr):
        self.buffer.append(data)


async def cli(buffer):
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    stdin_transport, protocol = await loop.connect_read_pipe(
        lambda: protocol, sys.stdin
    )
    while True:
        print("> ", end="", flush=True)
        line = await reader.readline()
        line = line.decode().strip()
        if line == "q":
            stdin_transport.close()
            loop.stop()
            break
        elif line == "ls":
            print("data received:", len(buffer))
            for b in buffer:
                print(b)


def main():
    loop = asyncio.new_event_loop()
    buffer = []
    task = loop.create_datagram_endpoint(
        lambda: ClientProtocol(buffer), remote_addr=("127.0.0.1", 53000)
    )
    udp_transport, protocol = loop.run_until_complete(task)
    loop.run_until_complete(cli(buffer))
    loop.run_forever()

    print("\nbye.")


if __name__ == "__main__":
    main()
