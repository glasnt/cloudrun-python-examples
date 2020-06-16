import falcon
class HelloResource:

    def on_get(self, req, resp):
        resp.body = "Hello Falcon, with love from gunicorn"


app = falcon.API()
app.add_route('/', HelloResource())
