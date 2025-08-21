
This project was created when I wanted to play on a Minecraft server with my friends.  
We built an arena, but to reset it we had to manually work on a remote server.  
To simplify this process, I wrote this script — my first project where I used **SFTP**.

Features
- Manage map resets via a **Telegram bot**.
- Store multiple maps and switch between them.
- Simple configuration with `.env`.
- First experience using **Paramiko** for SFTP connections.

Installation
````bash
git clone https://github.com/yourusername/map_reseter.git
cd map_reseter
````

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate   # On Linux/Mac
.venv\Scripts\activate      # On Windows
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the root directory:

```
BOT_TOKEN = your_telegram_bot_token
HOST = your.server.com
PORT = port
USER = username
PASSWORD = password
```

---

## Project Structure

```
map_reseter/
│
├── bot/                  # Telegram bot logic
│   ├── bot.py            # Telegram bot file  
│   └── utils/             # Bot-specific data
│       └── bot_ulits.json # Additional functions for bot
│
├── data/             # Bot-specific data
│   └── configs.json
│
├── maps/                 # Example maps
│   ├── first_map_example/
│   └── second_map_example/
│
├── utils/                # Utility modules
│   ├── server_utils.py
│   └── storage_utils.py
│
├── config.py             # Configuration loader
├── main.py               # Entry point
├── myapp.log             # Log file
├── .gitignore
└── README.md
```

---

## Usage

Run the bot:

```bash
python main.py
```

Then, in Telegram, use commands like:

* `/start`
* `/add "local folder" "remote folder"`
* `/remove N`
* `/list`

---
