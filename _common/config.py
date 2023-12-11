import os
from pathlib import Path

import deepmerge
import pulumi

from _common.import_module import import_module
from _common.naming import get_logical_name
from _data.backup.script.postgres import gen_postgres_backup_restore_script


def __build_config(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker_config = __build_config("docker")
server_config = __build_config("server")
dns_config = __build_config("dns")
storage_config = __build_config("storage")
service_config = __build_config("service")

redis_config = storage_config.get("redis", [])
postgres_config = storage_config.get("postgres", {})
mariadb_config = storage_config.get("mariadb", {})


def __build_volume_config():
    __config = storage_config.get("volume", {})
    if "local" not in __config:
        __config["local"] = {}
    __config["local"] |= {"redis-{}-data".format(db): None for db in redis_config}
    __config["local"] |= {
        "postgres-{}-data".format(db): None for db in postgres_config.keys()
    }
    __config["local"] |= {
        "mariadb-{}-data".format(db): None for db in mariadb_config.keys()
    }
    __config["local"] |= {"postgres-backup": None}
    return __config


volume_config = __build_volume_config()


def __build_container_storage():
    __config = storage_config.get("container", {})
    __docker_browser_volumes = set()

    for ks, vs in __config.items():
        for kc, vc in vs.items():
            if "volume" not in vc:
                volume = "{}-{}".format(ks, kc)
                assert volume in volume_config.get("local", {})
                vc["volume"] = volume
            __docker_browser_volumes.add(vc["volume"])

    for db in redis_config:
        container = "redis-{}".format(db)
        __config[container] = {
            "data": {"dir": "/data/", "volume": "{}-data".format(container)}
        }
    for db in postgres_config.keys():
        container = "postgres-{}".format(db)
        __config[container] = {
            "data": {
                "dir": "/var/lib/postgresql/data/",
                "volume": "{}-data".format(container),
            },
            "backup": {
                "dir": "/backup/",
                "volume": "postgres-backup",
            },
        }
    for db in mariadb_config.keys():
        container = "maria-{}".format(db)
        __config[container] = {
            "data": {
                "dir": "/var/lib/mysql/",
                "volume": "{}-data".format(container),
            },
        }

    __docker_browser_config = service_config["docker-browser"]
    __docker_browser_mount_root = Path(__docker_browser_config["mount-root"])
    __docker_browser_mount_secondary = (
        __docker_browser_mount_root / __docker_browser_config["mount-secondary"]
    )

    __docker_browser_mount_rw = set(__docker_browser_config.get("rw", []))
    __docker_browser_mount_top = __docker_browser_mount_rw | set(
        __docker_browser_config.get("top", [])
    )

    __config["docker-browser"] = {
        v: {
            "dir": os.fspath(
                (
                    __docker_browser_mount_root
                    if v in __docker_browser_mount_top
                    else __docker_browser_mount_secondary
                )
                / v
            ),
            "volume": v,
            "ro": False if v in __docker_browser_mount_rw else True,
        }
        for v in __docker_browser_volumes
    }
    return __config


def __build_backup():
    __config = storage_config.get("backup", {})
    __config["common"]["host"] = get_logical_name()

    for ks, vs in __config.get("service", {}).items():
        stops = vs.pop("stop", [])
        vs["stop"] = [get_logical_name(stop) for stop in stops]

        volume_dict = {}
        for kc, vc in vs.pop("volume", {}).items():
            if kc not in volume_config.get("local", {}):
                kc = "{}-{}".format(ks, kc)

            if "script_path" in vc:
                script_config = import_module(Path(vc.pop("script_path"))).script_config
                vc |= script_config

            volume_dict[kc] = vc

        if vs.pop("postgres", False):
            volume_dict["postgres-backup"] = gen_postgres_backup_restore_script(ks)

        vs["volume"] = volume_dict

    return __config


def __build_secret():
    __config = __build_config("secret_")
    __config["key"] = __config.get("key", {})

    __config["key"] |= {
        "postgres-{}".format(db): {"special": False} for db in postgres_config.keys()
    }

    return __config


storage_config["aws"] = {
    "AWS_ACCESS_KEY_ID": storage_config["key-id"],
    "AWS_SECRET_ACCESS_KEY": storage_config["key-secret"],
    "S3_ENDPOINT": storage_config["endpoint"],
    "S3_BUCKET": storage_config["bucket"],
}

container_storage_config = __build_container_storage()

backup_config = __build_backup()

secret_config = __build_secret()
