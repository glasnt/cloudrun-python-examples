from bottle import route, run


@route("/")
def hello():
    return "Hello Bottle, with love from gunicorn."


if __name__ == "__main__":
    run(host="localhost", port=8080)
