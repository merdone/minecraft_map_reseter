import asyncio
import json
import logging
from pathlib import Path
from os import getenv

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from main import sftp_connect, delete_files, copy_files

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
CONFIG_PATH = DATA_DIR / "configs.json"  # { "<user_id>": [{"local":"...", "remote":"..."}] }

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
logging.basicConfig(
    filename='myapp.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)


def load_storage() -> dict:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def save_storage(data: dict):
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_config(user_id: int, local: str, remote: str):
    data = load_storage()
    arr = data.get(str(user_id), [])
    if not any(c["local"] == local and c["remote"] == remote for c in arr):
        arr.append({"local": local, "remote": remote})
    data[str(user_id)] = arr
    save_storage(data)


def get_configs(user_id: int):
    return load_storage().get(str(user_id), [])


def remove_config(user_id: int, index: int) -> bool:
    data = load_storage()
    arr = data.get(str(user_id), [])
    if 0 <= index < len(arr):
        arr.pop(index)
        data[str(user_id)] = arr
        save_storage(data)
        return True
    return False


def parse_quoted_args(text: str):
    parts = []
    current = []
    in_quotes = False
    for char in text:
        if char == '"':
            in_quotes = not in_quotes
            if not in_quotes:
                parts.append("".join(current).strip())
                current = []
        else:
            if in_quotes:
                current.append(char)
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None


def build_main_kb(configs):
    rows = []

    for i, cfg in enumerate(configs):
        title = f"▶️ {cfg['local']} → {cfg['remote']} (#{i})"
        rows.append([KeyboardButton(text=title)])

    rows.append([KeyboardButton(text="➕ Add"),
                 KeyboardButton(text="🗂 List")])
    rows.append([KeyboardButton(text="❌ Remove")])

    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def deploy_config(message: Message, cfg: dict):
    """connect to server and deploy"""
    await message.answer(
        f"• local: <code>{html.quote(cfg['local'])}</code>\n"
        f"• remote: <code>{html.quote(cfg['remote'])}</code>"
    )

    HOST = getenv("HOST")
    PORT = int(getenv("PORT"))
    USER = getenv("USER")
    PASSWORD = getenv("PASSWORD")

    with sftp_connect(HOST, PORT, USER, PASSWORD) as sftp:
        delete_files(sftp, "second_map")
        copy_files(sftp, "second_map_example", "second_map")
    # TODO: вызови свой деплой здесь


@dp.message(CommandStart())
async def on_start(message: Message):
    """start command"""

    configs = get_configs(message.from_user.id)
    kb = build_main_kb(configs)

    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}!\n"
        f"To add new maps setups:\n"
        f'<code>/add "local_name" "virtual_name"</code>',
        reply_markup=kb
    )


@dp.message(Command("add"))
async def cmd_add(message: Message):
    """add map setup to config"""

    parsed = parse_quoted_args(message.text or "")

    if not parsed:
        return await message.answer(
            "Формат:\n"
            '<code>/add "локальная_папка" "виртуальная_папка"</code>\n'
            "пример:\n"
            '<code>/add "second_map_example" "second_map"</code>',
            reply_markup=build_main_kb(get_configs(message.from_user.id))
        )

    local, remote = parsed
    add_config(message.from_user.id, local, remote)

    configs = get_configs(message.from_user.id)
    await message.answer(
        "Added ✅",
        reply_markup=build_main_kb(configs)
    )



@dp.message(Command("list"))
async def cmd_list(message: Message):
    """show list of the configs"""

    configs = get_configs(message.from_user.id)
    kb = build_main_kb(configs)

    if not configs:
        return await message.answer(
            "No maps in config. You can add it using /add.",
            reply_markup=kb  # <-- важно: прислать новую раскладку
        )

    text = "\n".join(
        [f"#{index}: local={html.quote(element['local'])}  →  remote={html.quote(element['remote'])}"
         for index, element in enumerate(configs)]
    )

    await message.answer(text, reply_markup=kb)


@dp.message(Command("remove"))
async def cmd_remove(message: Message):
    """remove map from config"""

    parts = (message.text or "").split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await message.answer(
            'Format: <code>/remove N</code>, for example: <code>/remove 0</code>',
            reply_markup=build_main_kb(get_configs(message.from_user.id))
        )

    index = int(parts[1])
    is_deleted_from_config = remove_config(message.from_user.id, index)
    configs = get_configs(message.from_user.id)

    if not is_deleted_from_config:
        return await message.answer(
            "Incorrect index",
            reply_markup=build_main_kb(configs)
        )

    return await message.answer(
        "Deleted ✅",
        reply_markup=build_main_kb(configs)
    )



# ====== BUTTONS ======
@dp.message(F.text.startswith("▶️ "))
async def on_deploy_button(message: Message):
    txt = message.text

    try:
        index_str = txt.split("(#")[-1].split(")")[0]
        cfgs = get_configs(message.from_user.id)
        cfg = cfgs[int(index_str)]

    except Exception as e:
        return await message.answer("Не смог определить конфигурацию 🤔")

    await deploy_config(message, cfg)


@dp.message(F.text == "🗂 List")
async def btn_list(message: Message):
    await cmd_list(message)


@dp.message(F.text == "➕ Add")
async def btn_add_hint(message: Message):
    await message.answer(
        "Добавь конфигурацию так:\n"
        '<code>/add "локальная_папка" "виртуальная_папка"</code>\n'
        "пример:\n"
        '<code>/add "second_map_example" "second_map"</code>'
    )


@dp.message(F.text == "❌ Remove")
async def btn_remove_hint(message: Message):
    await message.answer('For remove you can use:\n<code>/remove N</code>\nнапример: <code>/remove 0</code>')


# ====== BOOT ======
async def main():
    if not TOKEN:
        raise SystemExit("BOT_TOKEN не задан в .env")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
