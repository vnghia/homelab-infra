import json
import os
import uuid

import pykeepass
from pykeepass.entry import Entry

from _secret.keepass.common import make_lock


@make_lock
def main():
    kp = pykeepass.PyKeePass(
        os.environ["KEEPASS_DATABASE"],
        os.environ.get("KEEPASS_PASSWORD"),
        os.environ.get("KEEPASS_KEY"),
    )
    entry_data = json.loads(input())

    entry: Entry | None = kp.find_entries(
        uuid=uuid.UUID(hex=os.environ["PULUMI_COMMAND_STDOUT"]), first=True
    )
    assert entry

    if entry.username != entry_data["username"]:
        entry.username = entry_data["username"]

    if entry.password != entry_data["password"]:
        entry.password = entry_data["password"]

    if entry.url != entry_data.get("url"):
        entry.url = entry_data.get("url")

    if "tags" in entry_data:
        if entry.tags != entry_data["tags"]:
            entry.tags = entry_data["tags"]
    else:
        entry.tags = None

    custom_data = entry_data.get("custom", {})
    for k, v in custom_data.items():
        old = entry.get_custom_property(k)
        if old != v:
            entry.set_custom_property(k, v)
    old_properties = entry.custom_properties.keys()
    for property in old_properties:
        if property not in custom_data:
            entry.delete_custom_property(property)

    kp.save()
    print(entry.uuid.hex)


if __name__ == "__main__":
    main()
