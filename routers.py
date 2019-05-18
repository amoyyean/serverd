from tornado.web import URLSpec

from handlers import IndexHandler, DeployHandler, RunnerHandler


router = [
    URLSpec('/api/v1/?', IndexHandler, name='index'),
    URLSpec('/api/v1/deploy/?', DeployHandler, name='deploy'),
    URLSpec('/api/v1/runner/?', RunnerHandler, name='runner'),
]
