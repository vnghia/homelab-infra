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
        uuid=uuid.UUID(hex=os.environ["PULUMI_COMMAND_STDOUT"]), first=True
    )
    if group:
        kp.delete_group(group)
        kp.save()


if __name__ == "__main__":
    main()
