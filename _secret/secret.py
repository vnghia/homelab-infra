import hashlib
from pathlib import Path

import pulumi
import pulumi_random as random
from pulumi import Output, ResourceOptions

from _command import Command
from _common import constant, get_logical_name, secret_config
from _network.dns import hostnames
from _secret.resource import child_opts


class Secret:
    def __init__(self) -> None:
        self.keys = {}
        self.__usernames = {}
        self.__passwords = {}
        self.__keepass_entries = {}
        self.accounts = {}
        self.authelia_accounts = {}

        self.__build_key()
        self.__build_keepass_group()
        self.__build_keepass_entry()

    def __build_key(self):
        for full_name, config in secret_config.pop("key", {}).items():
            name = full_name.removeprefix("__")
            self.keys[name] = self.build_password(
                "{}-key".format(name),
                protect=not full_name.startswith("__"),
                **({"length": 64} | (config or {})),
            )

    def __build_keepass_group(self):
        self.__keepass_group = Command.build(
            name="keepass-group",
            opts=child_opts.merge(ResourceOptions(delete_before_replace=True)),
            create=Path(__file__).parent / "keepass" / "group" / "create.py",
            delete=Path(__file__).parent / "keepass" / "group" / "delete.py",
            environment={
                "KEEPASS_ROOT_GROUP": secret_config["keepass"]["root"],
                "KEEPASS_GROUP_NAME": get_logical_name(),
            },
        )
        self.__keepass_group_uuid = self.__keepass_group.stdout
        self.__keepass_entry_opts = ResourceOptions(
            parent=self.__keepass_group, delete_before_replace=True
        )

    def __build_keepass_entry(self):
        common_sha256 = hashlib.file_digest(
            open(Path(__file__).parent / "keepass" / "common.py", "rb"), "sha256"
        ).hexdigest()

        for name, config in secret_config.pop("account", {}).items():
            config = config or {}

            config["title"] = name

            username = config.get("username")
            if not username:
                use_email = config.pop("email", False)
                if not use_email:
                    self.__usernames[name] = self.build_string(
                        "{}-account".format(name), opts=self.__keepass_entry_opts
                    )
                    username = self.__usernames[name].result
                else:
                    self.__usernames[name] = Output.format(
                        "{0}@{1}",
                        self.build_string(
                            "{}-account".format(name), opts=self.__keepass_entry_opts
                        ).result,
                        hostnames[config["hostname"]],
                    )
                    username = self.__usernames[name]
            config["username"] = username

            password = config.pop("password", {})
            if not isinstance(password, str):
                self.__passwords[name] = self.build_password(
                    "{}-account".format(name),
                    opts=self.__keepass_entry_opts,
                    **password
                )
                password = self.__passwords[name].result
            config["password"] = password

            hostname = hostnames.get(config.pop("hostname", None), None)
            if hostname:
                config["url"] = Output.concat("https://", hostname)
            config["tags"] = config.pop("tags", []) + [
                "{}.{}".format(k, v) for k, v in constant.PROJECT_TAG.items()
            ]

            if config.pop("authelia", False):
                authelia_hostname = hostnames["public-authelia"]
                config["url"] = Output.concat("https://", authelia_hostname)
                username = config["username"]
                self.authelia_accounts[name] = {
                    "username": username,
                    "displayname": config.get("displayname", username),
                    "email": Output.format("{0}@{1}", username, authelia_hostname),
                    "password": config["password"],
                    "groups": config.get("groups", []),
                }

            self.__keepass_entries[name] = Command.build(
                name="{}-keepass-entry".format(name),
                opts=self.__keepass_entry_opts,
                create=Path(__file__).parent / "keepass" / "entry" / "create.py",
                delete=Path(__file__).parent / "keepass" / "entry" / "delete.py",
                update=Path(__file__).parent / "keepass" / "entry" / "update.py",
                stdin=Output.json_dumps(config),
                environment={
                    "KEEPASS_GROUP_UUID": self.__keepass_group_uuid,
                    "__KEEPASS_COMMON_SHA256": common_sha256,
                },
            )

            self.accounts[name] = {
                "username": config["username"],
                "password": config["password"],
            }
            if name in self.__passwords:
                self.accounts[name]["bcrypt"] = self.__passwords[name].bcrypt_hash

    @classmethod
    def build_password(
        cls,
        name: str,
        opts: ResourceOptions | None = None,
        export: bool = False,
        protect: bool = True,
        **kwargs
    ):
        special = kwargs.pop("special", True)
        password = random.RandomPassword(
            name,
            opts=(opts or child_opts).merge(ResourceOptions(protect=protect)),
            length=kwargs.pop("length", 32),
            min_lower=kwargs.pop("min_lower", 1),
            min_numeric=kwargs.pop("min_numeric", 1),
            min_special=kwargs.pop("min_special", 1 if special else 0),
            min_upper=kwargs.pop("min_upper", 1),
            special=special,
            **kwargs
        )
        if export:
            pulumi.export(name, password.result)
        return password

    @classmethod
    def build_string(cls, name: str, opts: ResourceOptions | None = None, **kwargs):
        return random.RandomString(
            name,
            opts=(opts or child_opts),
            length=kwargs.pop("length", 8),
            min_lower=kwargs.pop("min_lower", 1),
            min_numeric=kwargs.pop("min_numeric", 1),
            min_special=kwargs.pop("min_special", 0),
            min_upper=kwargs.pop("min_upper", 1),
            special=kwargs.pop("special", False),
            **kwargs
        )


secret = Secret()
