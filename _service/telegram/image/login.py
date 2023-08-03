import json
import os
import shutil
from pathlib import Path

from telethon.sync import TelegramClient

telegram_config = json.loads(os.environ["TELEGRAM_CONFIG"])

telegram_api_id = telegram_config["api"]["id"]
telegram_api_hash = telegram_config["api"]["hash"]
telegram_session_dir = Path(telegram_config["session"])


async def login(client: TelegramClient):
    me = await client.get_me(input_peer=True)
    user_id = me.user_id
    telegram_session_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(
        "login.session", telegram_session_dir / "{}.session".format(user_id)
    )


def main():
    client = TelegramClient("login", telegram_api_id, telegram_api_hash)
    with client:
        client.loop.run_until_complete(login(client))


if __name__ == "__main__":
    main()
