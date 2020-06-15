import hug

@hug.get("/")
def hello():
    return "Hello Hug, with love from uwsgi."

