import asyncio
from config import load_config
from bot.bot import main as bot_main

if __name__ == "__main__":
    config = load_config()
    asyncio.run(bot_main(config))