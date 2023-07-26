import json
import os
import uuid

import pykeepass


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
    entry = kp.add_entry(
        group,
        entry_data.pop("title"),
        entry_data.pop("username"),
        entry_data.pop("password"),
        **entry_data
    )
    for k, v in entry_data.get("custom", {}).items():
        entry.set_custom_property(k, v)
    kp.save()
    print(entry.uuid.hex)


if __name__ == "__main__":
    main()
