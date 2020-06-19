from aiohttp import web

async def index(request):
    return web.Response(text="👋 Hello aiohttp - gunicorn")


async def myapp():
    app = web.Application()
    app.router.add_get('/', index)
    return app
