import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.routers import router
from settings import TORTOISE_ORM


app = FastAPI()
register_tortoise(app, config=TORTOISE_ORM)
# app.add_middleware(GZipMiddleware)
app.include_router(router)


if __name__ == "__main__":
    SERVEICE_HOST_IP = "0.0.0.0"
    SERVICE_HOST_PORT = "8000"
    uvicorn.run(
        "main:app",
        host=SERVEICE_HOST_IP,
        port=int(SERVICE_HOST_PORT),
        access_log=True,
        workers=1,
    )
