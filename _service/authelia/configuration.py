import os
from pathlib import Path

from _common import container_storage_config, get_logical_name, service_config
from _data.postgres import postgres
from _data.redis import redis
from _network.dns.hostnames import hostnames
from _secret import secret

_ntfy_config = service_config["ntfy"]

_redis_config = redis.db["authelia"]
_postgres_config = postgres.db["authelia"]
_authelia_volume = container_storage_config["authelia"]

_authelia_url = hostnames["public-authelia"]

output_config = {
    "type": "yaml",
    "name": "authelia-config",
    "volume": _authelia_volume["config"]["volume"],
    "path": "configuration.yml",
    "input": {
        "theme": "auto",
        "identity_validation": {
            "reset_password": {
                "jwt_secret": secret.keys["authelia-jwt"].result,
            }
        },
        "authentication_backend": {
            "password_reset": {"disable": True},
            "file": {
                "path": os.fspath(Path(_authelia_volume["config"]["dir"]) / "users.yml")
            },
        },
        "access_control": {
            "default_policy": "deny",
            "rules": [
                {"domain_regex": [".*"], "policy": "bypass", "methods": ["OPTIONS"]}
            ],
        },
        "session": {
            "secret": secret.keys["authelia-session"].result,
            "cookies": [
                {
                    "domain": _authelia_url,
                    "authelia_url": "https://" + _authelia_url,
                    "remember_me": -1,
                }
            ],
            "redis": {
                "host": _redis_config["host"],
                "port": _redis_config["port"],
                "username": _redis_config["username"],
                "password": _redis_config["password"],
            },
        },
        "storage": {
            "encryption_key": secret.keys["authelia-storage-encryption"].result,
            "postgres": {
                "address": "{}:{}".format(
                    _postgres_config["host"], _postgres_config["port"]
                ),
                "username": _postgres_config["username"],
                "password": _postgres_config["password"],
                "database": _postgres_config["database"],
            },
        },
        "notifier": {
            "smtp": {
                "address": "{}:{}".format(hostnames["private-mailserver"], 25),
                "sender": "notification@{}".format(
                    hostnames[_ntfy_config["email-server"]["service"]["authelia"]]
                ),
            }
        },
        "totp": {"issuer": get_logical_name()},
    },
}
