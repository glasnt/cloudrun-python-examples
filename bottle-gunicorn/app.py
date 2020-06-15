import bottle

app = bottle.default_app()


@bottle.route("/")
def hello():
    return "Hello Bottle, with love from gunicorn."


if __name__ == "__main__":
    bottle.run(host="localhost", port=8080)

