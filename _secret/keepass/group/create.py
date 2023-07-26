import os

import pykeepass


def main():
    kp = pykeepass.PyKeePass(
        os.environ["KEEPASS_DATABASE"],
        os.environ.get("KEEPASS_PASSWORD"),
        os.environ.get("KEEPASS_KEY"),
    )
    root_group = kp.find_groups(
        path=os.environ["KEEPASS_ROOT_GROUP"].split("/"), first=True
    )
    group = kp.add_group(root_group, os.environ["KEEPASS_GROUP_NAME"])
    kp.save()
    print(group.uuid.hex)


if __name__ == "__main__":
    main()
