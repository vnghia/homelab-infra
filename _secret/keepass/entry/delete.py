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
    entry = kp.find_entries(
        uuid=uuid.UUID(hex=os.environ["PULUMI_COMMAND_STDOUT"]), first=True
    )
    if entry:
        kp.delete_entry(entry)
        kp.save()


if __name__ == "__main__":
    main()
