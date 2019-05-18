import tornado.ioloop
import tornado.web

from routers import router


if __name__ == "__main__":
    app = tornado.web.Application(router, debug=True)
    app.listen(8888)
    # http://localhost:8888/api/v1
    tornado.ioloop.IOLoop.current().start()
