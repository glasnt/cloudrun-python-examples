from starlette.responses import HTMLResponse

async def app(scope, receive, send):
    assert scope['type'] == 'http'
    resp = HTMLResponse(f"Hello Starlette, from uvicorn")
    await resp(scope, receive, send)

