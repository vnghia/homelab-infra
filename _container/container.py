import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions

from _common import (
    constant,
    container_storage_config,
    docker_config,
    get_logical_name,
    server_config,
)
from _data.docker import volume_map
from _image import docker_image
from _network.docker import default_bridge_network


class DockerContainer:
    @classmethod
    def build(
        cls,
        name: str,
        opts: ResourceOptions,
        image: str | None = None,
        envs: dict[Input[str], Input[str]] | None = None,
        volumes: dict[Input[str], dict] | None = None,
        **kwargs,
    ):
        envs = {"TZ": server_config["tz"]} | docker_config.get("env", {}) | (envs or {})
        if len(envs):
            kwargs["envs"] = []
            for k, v in envs.items():
                kwargs["envs"].append(
                    Output.concat(k, "=", Output.from_input(v).apply(str))
                )

        if not ("network_mode" in kwargs or "networks_advanced" in kwargs):
            kwargs["networks_advanced"] = [
                docker.ContainerNetworksAdvancedArgs(
                    name=default_bridge_network.name,
                    aliases=[name] + kwargs.pop("network_aliases", []),
                )
            ]

        volume_args = kwargs.pop("_volumes", [])
        if name in container_storage_config:
            for volume in container_storage_config[name].values():
                volume_args.append(
                    docker.ContainerVolumeArgs(
                        container_path=volume["dir"],
                        read_only=volume.get("ro", False),
                        volume_name=volume_map.get(volume["volume"]),
                    )
                )
        if volumes:
            for container_path, volume in volumes.items():
                host_path = volume.get("host", container_path)
                read_only = volume.get("ro", False)
                volume_args.append(
                    docker.ContainerVolumeArgs(
                        container_path=container_path,
                        host_path=host_path,
                        read_only=read_only,
                    )
                )
        if len(volume_args):
            kwargs["volumes"] = volume_args

        image_data = docker_image.image_map[image or name]

        return docker.Container(
            get_logical_name(name),
            opts=opts.merge(
                ResourceOptions(delete_before_replace=True, ignore_changes=["image"])
            ),
            name=get_logical_name(name),
            image=image_data["image_name"],
            restart=kwargs.pop("restart", "unless-stopped"),
            rm=kwargs.pop("rm", False),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in constant.PROJECT_TAG.items()
            ]
            + [
                docker.ContainerLabelArgs(
                    label="image.id", value=image_data["image_id"]
                )
            ]
            + [
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in kwargs.pop("labels", {}).items()
            ],
            **kwargs,
        )
