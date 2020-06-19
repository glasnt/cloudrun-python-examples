import bottle

app = bottle.default_app()


@bottle.route("/")
def hello():
    return "👋 Hello bottle - gunicorn"


if __name__ == "__main__":
    bottle.run(host="localhost", port=8080)

