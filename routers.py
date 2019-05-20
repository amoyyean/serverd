"""路由配置"""
from tornado.web import URLSpec

from handlers import IndexHandler, DeployHandler, RunnerHandler, RegHandler


router = [
    URLSpec('/api/v1/?', IndexHandler, name='index'),
    URLSpec('/api/v1/deploy/?', DeployHandler, name='deploy'),
    URLSpec('/api/v1/runner/?', RunnerHandler, name='runner'),
    URLSpec('/api/v1/reg/?', RegHandler, name='reg'),
]
