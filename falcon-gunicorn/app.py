import falcon
class HelloResource:

    def on_get(self, req, resp):
        resp.body = "👋 Hello falcon - gunicorn"


app = falcon.API()
app.add_route('/', HelloResource())
