import json
import os
import typing
from contextlib import contextmanager
from pathlib import Path

import docker
import typed_argparse as tap

import _file

__backup_config: dict[str, dict] = json.loads(os.environ["BACKUP_CONFIG"])

backup_common_config = __backup_config.pop("common")
backup_service_config = __backup_config.pop("service")
service_list = list(backup_service_config.keys())

mount_path_prefix = Path(backup_common_config["prefix"])
backup_host = backup_common_config["host"]

docker_client = docker.from_env()


@contextmanager
def stop_container(container_name: list[str]):
    containers = []
    for name in container_name:
        container = docker_client.containers.get(name)
        container.stop()
        containers.append(container)
    try:
        yield
    finally:
        for container in reversed(containers):
            container.start()


class ServiceArgs(tap.TypedArgs):
    services: list[typing.Literal[tuple(service_list)]] = tap.arg(
        "-s", "--service", nargs="+", default=service_list
    )


class BackupArgs(ServiceArgs):
    pass


class RestoreArgs(ServiceArgs):
    snapshot: str = tap.arg(default="latest")


def __backup_and_restore(is_backup: bool, args: BackupArgs | RestoreArgs):
    exceptions = []
    failed_services = []

    service_config = {
        service: backup_service_config[service] for service in args.services
    }

    for service, config in service_config.items():
        action = "backing up" if is_backup else "restoring"
        print("**** running {} for {} ****\n".format(action, service), flush=True)

        with stop_container(config.get("stop", [])):
            for volume, data in config.get("volume", {}).items():
                try:
                    root_dir = mount_path_prefix / volume
                    tags = [service, volume] + data.get("tag", [])

                    if is_backup:
                        _file.backup(
                            paths=data["path"],
                            root_dir=root_dir,
                            host=backup_host,
                            tags=tags,
                            excludes=data.get("exclude"),
                        )
                    else:
                        _file.restore(
                            snapshot=args.snapshot,
                            host=backup_host,
                            tags=tags,
                        )

                except Exception as e:
                    failed_services.append(service)
                    exceptions.append(e)

        print("\n**** finish {} for {} ****\n".format(action, service), flush=True)

    if len(exceptions):
        message = "Backup of {} failed.".format(", ".join(failed_services))
        raise ExceptionGroup(message, exceptions)


def backup(args: BackupArgs):
    __backup_and_restore(True, args)


def restore(args: RestoreArgs):
    __backup_and_restore(False, args)


def main():
    tap.Parser(
        tap.SubParserGroup(
            tap.SubParser("backup", BackupArgs), tap.SubParser("restore", RestoreArgs)
        ),
    ).bind(backup, restore).run()


if __name__ == "__main__":
    main()
