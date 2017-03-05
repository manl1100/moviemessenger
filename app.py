from tornado.ioloop import IOLoop
from tornado.web import Application
from facebook import FacebookHandler


def make_app():
    return Application([
        (r"/webhook", FacebookHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(5000)
    IOLoop.current().start()
