import asyncio
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

import notification
from telethon.sync import TelegramClient, events

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram.login_code")

telegram_config = json.loads(os.environ["TELEGRAM_CONFIG"])

telegram_api_id = telegram_config["api"]["id"]
telegram_api_hash = telegram_config["api"]["hash"]
telegram_session_dir = Path(telegram_config["session"])

telegram_notification_config = telegram_config["notification"]
notification_topic = telegram_notification_config.pop("topic")
notification_icon = telegram_notification_config.pop("icon")


async def send_login_code(event):
    notification.publish(
        topic=notification_topic,
        message=event.pattern_match.group(1),
        title="Login code",
        icon=notification_icon,
        tags=["login-code"],
    )


async def log_user_information(client: TelegramClient):
    me = await client.get_me()
    logger.info(
        "Listening to login code for user (id={}, username={}, phone={})".format(
            me.id, me.username, me.phone
        )
    )


def main():
    loop = asyncio.get_event_loop()

    sessions_ro = list(telegram_session_dir.glob("*.session"))
    session_dir = tempfile.TemporaryDirectory("telegram")
    session_dir_path = Path(session_dir.name)

    clients: list[TelegramClient] = []
    sessions: list[Path] = []

    for session_ro in sessions_ro:
        session = session_dir_path / session_ro.name
        shutil.copyfile(session_ro, session)
        sessions.append(session)
        clients.append(TelegramClient(str(session), telegram_api_id, telegram_api_hash))

    for session, client in zip(sessions, clients):
        client.add_event_handler(
            send_login_code, events.NewMessage(pattern=r"^Login code: ([0-9]{5})\..+")
        )
        client.start()
        loop.create_task(log_user_information(client))

    loop.run_forever()


if __name__ == "__main__":
    main()
