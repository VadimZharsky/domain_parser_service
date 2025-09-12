import os
import pathlib

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Server(BaseModel):
    PORT: int = 5019


class Scraper(BaseModel):
    TASK_POOL_MAX: int = 5


class Db(BaseModel):
    URL: str = "sqlite+aiosqlite:///./scraper.db"


class Settings(BaseSettings):
    _ROOT_FOLDER = pathlib.Path(__file__).parent.parent

    model_config = SettingsConfigDict(
        env_file=os.path.join(_ROOT_FOLDER, ".env"), case_sensitive=False, env_nested_delimiter="__"
    )

    server: Server = Server()
    scraper: Scraper = Scraper()
    db: Db = Db()
