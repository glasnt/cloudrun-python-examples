from klein import Klein

app = Klein()

@app.route("/")
def hello(request):
    return "👋 Hello klein - twistd"

resource = app.resource
