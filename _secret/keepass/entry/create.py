import json
import os
import uuid

import pykeepass

from _secret.keepass.common import make_lock


@make_lock
def main():
    kp = pykeepass.PyKeePass(
        os.environ["KEEPASS_DATABASE"],
        os.environ.get("KEEPASS_PASSWORD"),
        os.environ.get("KEEPASS_KEY"),
    )
    group = kp.find_groups(
        uuid=uuid.UUID(hex=os.environ["KEEPASS_GROUP_UUID"]), first=True
    )
    entry_data = json.loads(input())
    custom_data = entry_data.pop("custom", {})
    entry = kp.add_entry(
        group,
        entry_data.pop("title"),
        entry_data.pop("username"),
        entry_data.pop("password"),
        **entry_data,
    )
    for k, v in custom_data.items():
        entry.set_custom_property(k, v)
    kp.save()
    print(entry.uuid.hex)


if __name__ == "__main__":
    main()
