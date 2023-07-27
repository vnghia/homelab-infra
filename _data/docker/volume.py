from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _command import Command
from _common import docker_config, get_logical_name, server_config, storage_config
from _data.docker.label import DOCKER_VOLUME_LABELS
from _data.resource import child_opts
from _file import Template
from _secret import secret


class DockerVolume(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:docker:Volume", "volume", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__volumes: dict[str, docker.Volume] = {}

        self.__build_local_volume()
        self.__build_bind_volume()
        self.__build_rclone_config()
        self.__build_rclone_plugin()
        self.__build_mount_volume()
        self.__build_crypt_volume()
        self.__build_combine_volume()

        self.volume_map = {k: v.name for k, v in self.__volumes.items()}
        self.register_outputs({"volume_map": self.volume_map})

    def __build_local_volume(self):
        volume_config = docker_config.get("volume", {})
        local_volume_config = volume_config.get("local", [])

        for name, config in local_volume_config.items():
            config = config or {}
            self.__volumes[name] = docker.Volume(
                get_logical_name(name),
                opts=self.__child_opts,
                driver="local",
                labels=DOCKER_VOLUME_LABELS
                + [
                    docker.VolumeLabelArgs(
                        label="{}-bcrypt-hash".format(key),
                        value=secret.keys[key].bcrypt_hash,
                    )
                    for key in config.get("key", [])
                ],
            )

    def __build_bind_volume(self):
        volume_config = docker_config.get("volume", {})
        bind_volume_config = volume_config.get("bind", {})

        for name, path in bind_volume_config.items():
            self.__volumes[name] = docker.Volume(
                get_logical_name(name),
                opts=self.__child_opts,
                driver="local",
                driver_opts={
                    "type": "none",
                    "o": "bind",
                    "device": path,
                },
                labels=DOCKER_VOLUME_LABELS,
            )

    def __build_rclone_config(self):
        self.__rclone_opts = ResourceOptions(
            parent=ComponentResource(
                "data:rclone:root", "rclone", None, self.__child_opts
            )
        )
        self.__rclone_config = Template().build(
            opts=self.__rclone_opts,
            module_path=Path(__file__).parent / "rclone" / "config.py",
            docker_asset_volume=self.__volumes["rclone-config"].name,
        )

    def __build_rclone_plugin(self):
        platform = server_config["platform"]
        plugin_tag = eval(
            storage_config["rclone"]["plugin"]["version"], {}, {"platform": platform}
        )

        self.__rclone_plugin = docker.Plugin(
            get_logical_name("rclone-volume-plugin"),
            opts=self.__rclone_opts.merge(ResourceOptions(delete_before_replace=True)),
            alias=self.__rclone_config["sha256"].apply(
                lambda sha256: "{}:{}".format(get_logical_name("rclone"), sha256[:7])
            ),
            name="rclone/docker-volume-rclone:{}".format(plugin_tag),
            grant_all_permissions=True,
        )

        self.rclone_plugin_alias = self.__rclone_plugin.alias
        self.rclone_config_path = self.__rclone_config["config"]["path"]

        # TODO: https://github.com/kreuzwerker/terraform-provider-docker/issues/108
        self.__rclone_plugin_command = Command.build(
            "rclone-plugin-command",
            opts=self.__rclone_opts.merge(ResourceOptions(delete_before_replace=True)),
            create=Path(__file__).parent / "rclone" / "enable_plugin.py",
            delete=Path(__file__).parent / "rclone" / "disable_plugin.py",
            environment={
                "PLUGIN_NAME": self.rclone_plugin_alias,
                "RCLONE_CONFIG": "/data/config/{}".format(self.rclone_config_path),
            },
        )

    def __build_mount_volume(self):
        bucket_name = storage_config["bucket"]

        volume_config = storage_config["rclone"].get("mount", {})
        for name, prefix in volume_config.items():
            self.__volumes["mount-{}".format(name)] = docker.Volume(
                get_logical_name("mount-{}".format(name)),
                opts=self.__rclone_opts,
                driver=self.__rclone_plugin.alias,
                driver_opts={"remote": "bucket:{}/{}".format(bucket_name, prefix)},
                labels=DOCKER_VOLUME_LABELS
                + [
                    docker.ContainerLabelArgs(
                        label="plugin.command.id", value=self.__rclone_plugin_command.id
                    ),
                ],
            )

    def __build_crypt_volume(self):
        bucket_name = storage_config["bucket"]

        volume_config = storage_config["rclone"].get("crypt", {})
        for name in volume_config.keys():
            self.__volumes["crypt-{}".format(name)] = docker.Volume(
                get_logical_name("crypt-{}".format(name)),
                opts=self.__rclone_opts,
                driver=self.__rclone_plugin.alias,
                driver_opts={"remote": "crypt-{}-{}:/".format(bucket_name, name)},
                labels=DOCKER_VOLUME_LABELS
                + [
                    docker.ContainerLabelArgs(
                        label="plugin.command.id", value=self.__rclone_plugin_command.id
                    ),
                ],
            )

    def __build_combine_volume(self):
        if "combine" in storage_config["rclone"]:
            self.__volumes["combine"] = docker.Volume(
                get_logical_name("combine"),
                opts=self.__rclone_opts,
                driver=self.__rclone_plugin.alias,
                driver_opts={"remote": "combine:/"},
                labels=DOCKER_VOLUME_LABELS
                + [
                    docker.ContainerLabelArgs(
                        label="plugin.command.id", value=self.__rclone_plugin_command.id
                    ),
                ],
            )


docker_volume = DockerVolume()
