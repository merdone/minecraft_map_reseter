# config.py
from dataclasses import dataclass
from os import getenv
from dotenv import load_dotenv

load_dotenv()  # подтянуть .env в окружение

@dataclass(frozen=True)
class Config:
    bot_token: str
    host: str
    port: int
    user: str
    password: str

def load_config() -> Config:
    token = getenv("BOT_TOKEN")
    host = getenv("HOST")
    port = int(getenv("PORT"))
    user = getenv("USER")
    password = getenv("PASSWORD")

    if not token:
        raise SystemExit("BOT_TOKEN is missing in .env")

    return Config(
        bot_token=token,
        host=host or "",
        port=port,
        user=user or "",
        password=password or "",
    )
