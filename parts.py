"""实现与子进程通信的进程协议
并且定义了一些功能性方法
"""
import sys
import asyncio
from datetime import datetime
from datetime import timedelta


def timedelta_format(period: timedelta):
    """ Timedelta to str for human
    example: '5 days and 18:08:15'
    """
    if isinstance(period, timedelta):
        value = period.total_seconds()
        minute, second = divmod(value, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        return "{day} days and {hour}:{minute}:{second}".format(
            day=int(day), hour=int(hour), minute=int(minute), second=round(second, 2))
    raise TypeError('Parameter period must be timedelta')


def argument2str(arguments):
    argument = {key: value[0].decode('utf8') for key, value in arguments.items()}
    return argument


class AsyncSubprocessProtocol(asyncio.SubprocessProtocol):
    """ 基于SubprocessProtocol实现与子进程通信的进程协议 """
    def __init__(self, exit_future):
        self.exit_future = exit_future
        self.output = bytearray()
        self.start = None
        self.end = None
        self.pid = None

    def connection_made(self, transport):
        # 在建立连接时调用，记录时间
        self.start = datetime.now()
        self.pid = transport.get_pid()

    def pipe_data_received(self, fd, data):
        self.output.extend(data)

    def process_exited(self):
        # 在子进程退出时调用，记录时间
        self.end = datetime.now()
        self.exit_future.set_result(True)


async def generator_process(executors, project, version, module):
    """ 创建子进程来运行指定的EGG """
    loop = asyncio.get_running_loop()
    exit_future = asyncio.Future(loop=loop)
    sup = lambda: AsyncSubprocessProtocol(exit_future)
    transport, protocol = await loop.subprocess_exec(
        sup, sys.executable, '-m', executors, project, version, module,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )
    await exit_future
    transport.close()
    # 获取标准输出
    out = bytes(protocol.output).decode('ascii').rstrip()
    # 获取启动时间
    start_time = protocol.start.strftime('%Y-%m-%d %H:%M:%S')
    # 获取结束时间
    end_time = protocol.end.strftime('%Y-%m-%d %H:%M:%S')
    # 计算运行时长
    runtime = timedelta_format(protocol.end - protocol.start)
    pid = protocol.pid
    return start_time, end_time, runtime, out, pid


