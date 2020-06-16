import os

import tornado.ioloop
import tornado.web

port = os.environ.get('PORT', 8080)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, from Tornado")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
