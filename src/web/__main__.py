import uvicorn

from config import settings


def main():
    uvicorn.run(
        "web.app:get_app",
        workers=settings.uvicorn.workers,
        host=settings.uvicorn.host,
        port=settings.uvicorn.port,
        reload=settings.uvicorn.reload,
        factory=True,
    )


if __name__ == "__main__":
    main()
