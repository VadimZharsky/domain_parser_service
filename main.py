import uvicorn

from application.app import App
from application.providers import DependenciesProvider


if __name__ == "__main__":
    provider = DependenciesProvider()
    app = App.create(provider)
    uvicorn.run(
        app=app, host="0.0.0.0", port=provider.config.server.PORT, log_level="info"
    )
