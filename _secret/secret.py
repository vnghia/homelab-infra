from pathlib import Path

import pulumi_random as random
from pulumi import Output, ResourceOptions

from _command import Command
from _common import constant, get_logical_name, secret_config
from _network.dns import hostnames
from _secret.resource import child_opts


class Secret:
    def __init__(self) -> None:
        self.keys = {}
        self.__passwords = {}
        self.__keepass_entries = {}
        self.accounts = {}

        self.__build_key()
        self.__build_keepass_group()
        self.__build_keepass_entry()

    def __build_key(self):
        for name, config in secret_config.pop("key", {}).items():
            self.keys[name] = self.build_password(
                "{}-key".format(name), **(config or {})
            )

    def __build_keepass_group(self):
        self.__keepass_group = Command.build(
            name="keepass-group",
            opts=child_opts,
            create=Path(__file__).parent / "keepass" / "group" / "create.py",
            delete=Path(__file__).parent / "keepass" / "group" / "delete.py",
            environment={
                "KEEPASS_ROOT_GROUP": secret_config["keepass"]["root"],
                "KEEPASS_GROUP_NAME": get_logical_name(),
            },
        )
        self.__keepass_group_uuid = self.__keepass_group.stdout
        self.__keepass_entry_opts = ResourceOptions(parent=self.__keepass_group)

    def __build_keepass_entry(self):
        for name, config in secret_config.pop("account", {}).items():
            config = config or {}

            password = config.pop("password", {})
            if not isinstance(password, str):
                self.__passwords[name] = self.build_password(
                    "{}-account".format(name),
                    opts=self.__keepass_entry_opts,
                    **password
                )
                password = self.__passwords[name].result

            config["title"] = name
            config["username"] = config.get("username", name)
            config["password"] = password
            hostname = hostnames.get(config.pop("hostname", None), None)
            if hostname:
                config["url"] = Output.concat("https://", hostname)
            config["tags"] = config.pop("tags", []) + [
                "{}.{}".format(k, v) for k, v in constant.PROJECT_TAG.items()
            ]

            self.__keepass_entries[name] = Command.build(
                name="{}-keepass-entry".format(name),
                opts=self.__keepass_entry_opts.merge(
                    ResourceOptions(replace_on_changes=["stdin"])
                ),
                create=Path(__file__).parent / "keepass" / "entry" / "create.py",
                delete=Path(__file__).parent / "keepass" / "entry" / "delete.py",
                stdin=Output.json_dumps(config),
                environment={"KEEPASS_GROUP_UUID": self.__keepass_group_uuid},
            )

            self.accounts[name] = {
                "username": config["username"],
                "password": config["password"],
            }
            if name in self.__passwords:
                self.accounts[name]["bcrypt"] = self.__passwords[name].bcrypt_hash

    @classmethod
    def build_password(cls, name: str, opts: ResourceOptions | None = None, **kwargs):
        return random.RandomPassword(
            name,
            opts=(opts or child_opts).merge(
                ResourceOptions(protect=constant.PROJECT_STACK != "dev")
            ),
            length=kwargs.pop("length", 32),
            min_lower=kwargs.pop("min_lower", 1),
            min_numeric=kwargs.pop("min_numeric", 1),
            min_special=kwargs.pop("min_special", 1),
            min_upper=kwargs.pop("min_upper", 1),
            **kwargs
        )


secret = Secret()
