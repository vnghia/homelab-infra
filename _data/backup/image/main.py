import json
import os
import subprocess
import typing
from contextlib import contextmanager
from pathlib import Path

import docker
import notification
import typed_argparse as tap

import _file

__backup_config: dict[str, dict] = json.loads(os.environ["BACKUP_CONFIG"])

backup_common_config = __backup_config.pop("common")
backup_service_config = __backup_config.pop("service")
service_list = list(backup_service_config.keys())

mount_path_prefix = Path(backup_common_config["prefix"])
backup_host = backup_common_config["host"]

notification_config = backup_common_config["notification"]
notification_topic = notification_config.pop("topic")
notification_title = notification_config.pop("title")

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


class PruneArgs(tap.TypedArgs):
    keep_last: int = tap.arg("-k", "--keep-last", default=14)


class CheckArgs(tap.TypedArgs):
    read_data: bool = tap.arg("-r", "--read-data", default=False)


def __backup_and_restore(is_backup: bool, args: BackupArgs | RestoreArgs):
    exceptions = []
    failed_services = []

    service_config = {
        service: backup_service_config[service] for service in args.services
    }

    for service, config in service_config.items():
        action = "backing up" if is_backup else "restoring"
        action_key = "backup" if is_backup else "restore"
        print("**** running {} for {} ****\n".format(action, service), flush=True)

        with stop_container(config.get("stop", [])):
            for volume, data in config.get("volume", {}).items():
                try:
                    root_dir = mount_path_prefix / volume
                    tags = [service, volume] + data.get("tag", [])

                    script_data = data.get("{}-script".format(action_key), {})

                    if "pre" in script_data:
                        print(
                            "**** running pre-{} for {} ****\n".format(
                                action_key, service
                            ),
                            flush=True,
                        )
                        for cmd in script_data["pre"]:
                            print("\n{}\n".format(cmd), flush=True)
                            subprocess.check_call(cmd)
                        print(
                            "**** finish pre-{} for {} ****\n".format(
                                action_key, service
                            ),
                            flush=True,
                        )

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

                    if "post" in script_data:
                        print(
                            "**** running post-{} for {} ****\n".format(
                                action_key, service
                            ),
                            flush=True,
                        )
                        for cmd in script_data["post"]:
                            print("\n{}\n".format(cmd), flush=True)
                            subprocess.check_call(cmd)
                        print(
                            "**** finish post-{} for {} ****\n".format(
                                action_key, service
                            ),
                            flush=True,
                        )

                except Exception as e:
                    failed_services.append(service)
                    exceptions.append(e)

        print("\n**** finish {} for {} ****\n".format(action, service), flush=True)

    notification.publish_with_status(
        topic=notification_topic,
        message="{} for {}".format(action, ", ".join(args.services)),
        title=notification_title,
        exceptions=exceptions,
        message_failed="{} for {}".format(action, ", ".join(failed_services)),
        **notification_config
    )


def backup(args: BackupArgs):
    __backup_and_restore(True, args)


def restore(args: RestoreArgs):
    __backup_and_restore(False, args)


def prune(args: PruneArgs):
    exceptions = []
    try:
        subprocess.check_call(
            [
                "restic",
                "forget",
                "--keep-last",
                str(args.keep_last),
                "--group-by",
                "path,tags",
                "--host",
                backup_host,
                "--prune",
            ]
        )
    except Exception as e:
        exceptions.append(e)
    notification.publish_with_status(
        topic=notification_topic,
        message="prune backup",
        title=notification_title,
        exceptions=exceptions,
        **notification_config
    )


def check(args: CheckArgs):
    exceptions = []
    try:
        subprocess.check_call(
            ["restic", "check"] + (["--read-data"] if args.read_data else [])
        )
    except Exception as e:
        exceptions.append(e)
    notification.publish_with_status(
        topic=notification_topic,
        message="check backup",
        title=notification_title,
        exceptions=exceptions,
        **notification_config
    )


def main():
    tap.Parser(
        tap.SubParserGroup(
            tap.SubParser("backup", BackupArgs),
            tap.SubParser("restore", RestoreArgs),
            tap.SubParser("prune", PruneArgs),
            tap.SubParser("check", CheckArgs),
        ),
    ).bind(backup, restore, prune, check).run()


if __name__ == "__main__":
    main()
