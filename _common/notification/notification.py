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
