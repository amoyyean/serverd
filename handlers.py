import time
import os
import sys
import asyncio
import aiofiles
import socket
from tornado.websocket import WebSocketHandler
from uuid import uuid1
from datetime import datetime
from bases import RestfulHandler
from parts import argument2str, generator_process
from settings import *


class IndexHandler(RestfulHandler):
    def get(self):
        arguments = argument2str(self.request.arguments)
        value = arguments.get('abs')
        self.write(value)


class DeployHandler(RestfulHandler):
    """项目部署，其实是文件上传功能"""
    async def post(self):
        arguments = argument2str(self.request.arguments)
        name = arguments.get('name')
        eggs = self.request.files.get('eggs')
        if not eggs:
            await self.interrupt(400, 'Egg file not found.')
        egg = eggs.pop()
        version = str(round(time.time()))  # filename is version
        path = PurePath.joinpath(EGG_DIR, name)
        if not os.path.exists(path):  # 如果目录不存在则创建
            os.makedirs(path)
        file = PurePath.joinpath(path, version + FILE_TYPE[0])
        async with aiofiles.open(file, 'wb') as f:  # 保存EGG文件
            await f.write(egg.get('body'))
        await self.over(201, {'message': 'successful', 'project': name, version: version})


class RunnerHandler(RestfulHandler):
    """即时调度"""
    async def post(self):
        arguments = argument2str(self.request.arguments)
        project = arguments.get('project')
        version = arguments.get('version')
        module = arguments.get('module')
        # 先响应请求
        await self.over(200, {'message': 'successful', 'project': project, version: version,
                              module: module})
        # low-level 创建进程来运行执行器 executors.py

        start, end, runtime, out, pid = await generator_process(EXECUTOR, project, version, module)

        # height-level创建进程来运行执行器 executors.py
        # process = await asyncio.create_subprocess_exec(sys.executable, '-m', 'executors.py',
        #                                                 stdout=asyncio.subprocess.PIPE)
        # pid = process.pid

        # 将日志写入文件
        path = PurePath.joinpath(LOG_DIR, project)
        if not os.path.exists(path):  # 如果目录不存在则创建
            os.makedirs(path)
        file = PurePath.joinpath(path, str(uuid1()) + FILE_TYPE[1])
        async with aiofiles.open(file, 'w') as f:  # 保存EGG文件
            await f.write(out)
        print(pid, out)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


class SchedulerHandler(RestfulHandler):
    """定时任务
    将Apscheduler库集成即可"""
    async def get(self):
        pass

    async def post(self):
        pass

    async def put(self):
        pass

    async def delete(self):
        pass


class RegisterHandler(WebSocketHandler):
    """多机注册
    允许其他服务器注册到主服务器"""

    def open(self):
        # 连接建立时验证身份并保存节点信息
        ssk = self.request.headers.get('Server-Secret-Key')
        port = self.request.headers.get('PORT')
        connected = socket.gethostname()
        host = socket.gethostbyname(connected) + ':' + port
        if ssk == SECRET_KEY:
            message = 'server master and server lite connected.'
            self.write_message(message)
            SERVERS[host] = self
        else:
            message = 'Server-Secret-Key 不匹配，断开连接。'
            self.write_message(message)
            self.close()
        print(SERVERS)

    def on_message(self, message):
        # 收到信息时调用
        self.write_message("Client Message: " + message)

    def on_close(self):
        print("WebSocket closed")


def send_to_server(client, message):
    # 向指定的客户端推送消息
    client.write_message(message)



