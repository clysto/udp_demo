# Python UDP Demo

这个项目使用 Python 实现了一个 UDP 服务端和一个 UDP 客户端。并且展示了如何 Graceful Shutdown UDP socket。

基本思想是使用 Python 中的 `select` 模块监听多个文件描述符：

```python
while True:
    readable, _, _ = select([self.socket, self.stop_pipe_r], [], [])
    if self.stop_pipe_r in readable:
        return
    for s in readable:
        _, self.client_addr = s.recvfrom(1)
        print("new client", self.client_addr)
```

当 select 的监听列表中的文件描述符有一个变为为可读状态时，select 函数从系统调用中唤醒。所以除了我们需要监听的 socket 文件描述符以外，我们可以构造一个管道描述符：

```python
self.stop_pipe_r, self.stop_pipe_w = os.pipe()
```

当程序需要关闭时，为了唤醒 select 系统调用，我们可以使用这个管道发送一个 dummy data，这样就可以使得 select 函数立即返回而不必等待下一个 socket 连接后再关闭服务器。

## Asynchronous I/O 版本

除此之外我还提供了使用 Python 中 `asyncio` 模块实现的 UDP 服务端和客户端。使用 `asyncio` 的好处是不必再使用多线程来进行 I/O 操作。