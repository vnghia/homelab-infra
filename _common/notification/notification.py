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
        headers={"Authorization": "Bearer {}".format(os.environ["NTFY_TOKEN"])},
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
        tags = kwargs.pop("tags", []) + ["rotating_light"]
        publish(
            topic=topic,
            message=message_failed,
            title=title,
            priority=5,
            tags=tags,
            **kwargs,
        )
        if len_exceptions > 1:
            raise ExceptionGroup(message_failed, exceptions)
        else:
            raise exceptions[0]
    else:
        tags = kwargs.pop("tags", []) + ["four_leaf_clover"]
        publish(
            topic=topic,
            message=message_success,
            title=title,
            tags=tags,
            **kwargs,
        )
