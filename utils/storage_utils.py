import json
from pathlib import Path

DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)
CONFIG_PATH = DATA_DIR / "configs.json"  # { "<user_id>": [{"local":"...", "remote":"..."}] }

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