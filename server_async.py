#!/usr/bin/env python3

import asyncio
import signal


class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, stop_event) -> None:
        super().__init__()
        self.client_addr = None
        self.stop = False
        self.stop_event = stop_event

    def connection_made(self, transport):
        self.transport = transport
        loop = asyncio.get_running_loop()
        loop.create_task(self.sender())

    def datagram_received(self, data, addr):
        print("new client", addr)
        self.client_addr = addr

    async def sender(self):
        while not self.stop:
            if self.client_addr is not None:
                print("send to", self.client_addr)
                self.transport.sendto(b"hello world\n", self.client_addr)
            await asyncio.wait(
                {self.stop_event},
                timeout=1,
            )


def main():
    loop = asyncio.new_event_loop()
    stop_event = loop.create_future()
    task = loop.create_datagram_endpoint(
        lambda: ServerProtocol(stop_event), local_addr=("127.0.0.1", 53000)
    )
    transport, protocol = loop.run_until_complete(task)

    def on_sigint():
        protocol.stop = True
        stop_event.set_result(True)
        loop.stop()

    loop.add_signal_handler(signal.SIGINT, on_sigint)
    loop.run_forever()
    tasks = asyncio.all_tasks(loop)
    for t in [t for t in tasks if not (t.done() or t.cancelled())]:
        loop.run_until_complete(t)
    transport.close()
    print("\nbye.")


if __name__ == "__main__":
    main()
