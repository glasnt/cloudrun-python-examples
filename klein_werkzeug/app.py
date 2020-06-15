from klein import Klein

app = Klein()

@app.route('/')
def hello(request):
    return 'Hello klein, with love from twistd'

resource = app.resource
