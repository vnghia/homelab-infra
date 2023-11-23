import random

from argon2 import PasswordHasher

from _common import container_storage_config
from _secret import secret

_authelia_volume = container_storage_config["authelia"]

ph = PasswordHasher()


def hash_password(password: str):
    random.seed(0)
    return ph.hash(password, salt=random.randbytes(256))


output_config = {
    "type": "yaml",
    "name": "authelia-users",
    "volume": _authelia_volume["config"]["volume"],
    "path": "users.yml",
    "input": {
        "users": {
            v.pop("username"): {
                "disabled": False,
                "password": v.pop("password").apply(hash_password),
            }
            | v
            for v in secret.authelia_accounts.values()
        }
    },
}
