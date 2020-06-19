from starlette.responses import HTMLResponse

async def app(scope, receive, send):
    assert scope['type'] == 'http'
    resp = HTMLResponse(f"👋 Hello starlette - uvicorn")
    await resp(scope, receive, send)

