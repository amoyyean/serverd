"""PYTHON 项目通用执行器"""
import os
import sys
import importlib

from tornado import ioloop

from settings import *


class Environment:
    """上下文管理器负责运行前的检查和善后处理"""
    def __init__(self, project, version):
        self.project = project
        self.version = version

    async def __aenter__(self):
        """事前准备
        如检查文件是否存在等操作"""
        egg = str(PurePath.joinpath(EGG_DIR, self.project, self.version + FILE_TYPE[0]))
        if os.path.isfile(egg):
            # 将文件路径添加到path
            sys.path.insert(0, egg)
        else:
            raise ValueError('EGG not found.')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """事后处理
        因demo中并无处理需求，所以pass"""
        pass


async def main():
    # 获取传入的参数
    project, version, module_name = sys.argv[-3:]
    sys.argv = sys.argv[:3]
    async with Environment(project, version):
        # 导包并运行固定的run方法
        module = importlib.import_module(module_name)
        module.run()


if __name__ == '__main__':
    loop = ioloop.IOLoop.instance()
    loop.run_sync(main)
