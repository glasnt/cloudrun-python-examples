from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello Flask, with love from gunicorn."


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
