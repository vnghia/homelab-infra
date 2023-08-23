import os

import httpx


def publish(
    topic: str,
    message: str,
    title: str,
    priority: int = 3,
    tags: list[str] | None = None,
    **kwargs,
):
    body = {"topic": topic, "title": title, "message": message, "priority": priority}
    if tags:
        body["tags"] = tags
    body.update(kwargs)

    httpx.post(
        os.environ["NTFY_ENDPOINT"],
        json=body,
        auth=(os.environ["NTFY_USERNAME"], os.environ["NTFY_PASSWORD"]),
    ).raise_for_status()


def publish_with_status(
    topic: str,
    message: str,
    title: str,
    exceptions: list[Exception],
    message_failed: str | None = None,
    **kwargs,
):
    message_success = "{} successful.".format(message)
    message_failed = "{} failed.".format(message_failed or message)
    len_exceptions = len(exceptions)
    if len_exceptions:
        publish(
            topic=topic,
            message=message_failed,
            title=title,
            priority=5,
            **kwargs,
        )
        if len_exceptions > 1:
            raise ExceptionGroup(message_failed, exceptions)
        else:
            raise exceptions[0]
    else:
        publish(
            topic=topic,
            message=message_success,
            title=title,
            **kwargs,
        )
