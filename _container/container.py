import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions

from _common import constant, docker_config, get_logical_name
from _container.image.image import docker_image
from _data.docker import volume_map
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
        **kwargs
    ):
        envs = docker_config.get("env") | (envs or {})
        if len(envs):
            kwargs["envs"] = []
            for k, v in envs.items():
                kwargs["envs"].append(Output.concat(k, "=", v))

        if not ("network_mode" in kwargs or "networks_advanced" in kwargs):
            kwargs["networks_advanced"] = [
                docker.ContainerNetworksAdvancedArgs(
                    name=default_bridge_network.name, aliases=[name]
                )
            ]

        volume_args = kwargs.pop("_volumes", [])
        if volumes:
            for container_path, volume in volumes.items():
                volume_name = volume_map.get(volume.get("name"))
                host_path = volume.get(
                    "host", container_path if volume_name is None else None
                )
                read_only = volume.get("ro", False)
                volume_args.append(
                    docker.ContainerVolumeArgs(
                        container_path=container_path,
                        host_path=host_path,
                        read_only=read_only,
                        volume_name=volume_name,
                    )
                )
        if len(volume_args):
            kwargs["volumes"] = volume_args

        image_data = docker_image.image_map[image or name]

        return docker.Container(
            get_logical_name(name),
            opts=opts.merge(ResourceOptions(ignore_changes=["image"])),
            image=image_data["image_name"],
            restart=kwargs.pop("restart", "unless-stopped"),
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
            **kwargs
        )