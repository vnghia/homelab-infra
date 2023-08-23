import asyncio
import json
import logging
import os
from pathlib import Path

import notification
from telethon.sync import TelegramClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram.refresh_session")

telegram_config = json.loads(os.environ["TELEGRAM_CONFIG"])

telegram_api_id = telegram_config["api"]["id"]
telegram_api_hash = telegram_config["api"]["hash"]
telegram_session_dir = Path(telegram_config["session"])

telegram_notification_config = telegram_config["notification"]
notification_topic = telegram_notification_config.pop("topic")
notification_icon = telegram_notification_config.pop("icon")


async def refresh_session(client: TelegramClient):
    me = await client.get_me()
    logger.info(
        "Refreshed session for user (id={}, username={}, phone={})".format(
            me.id, me.username, me.phone
        )
    )
    return me.username


def main():
    loop = asyncio.get_event_loop()

    sessions = list(telegram_session_dir.glob("*.session"))
    clients = [
        TelegramClient(str(session), telegram_api_id, telegram_api_hash)
        for session in sessions
    ]

    refresh_tasks = []
    for client in clients:
        client.start()
        refresh_tasks.append(loop.create_task(refresh_session(client)))

    results = loop.run_until_complete(
        asyncio.gather(*refresh_tasks, return_exceptions=True)
    )

    usernames = []
    exceptions = []
    for result in results:
        if isinstance(result, str):
            usernames.append(result)
        else:
            exceptions.append(result)

    notification.publish_with_status(
        topic=notification_topic,
        message="refresh session for {}".format(", ".join(usernames)),
        title="Refresh session",
        exceptions=exceptions,
        message_failed="refresh session",
        icon=notification_icon,
        tags=["refresh-session"],
    )


if __name__ == "__main__":
    main()
