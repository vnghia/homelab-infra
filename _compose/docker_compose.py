import json
from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import docker_config
from _data.docker import docker_volume
from _file import Template
from _network.docker import default_bridge_network

_compose_config = docker_config["compose"]


class DockerCompose(ComponentResource):
    def __init__(self) -> None:
        super().__init__("docker:index:Compose", "compose")

        self.__child_opts = ResourceOptions(parent=self)
        self.__compose_file = Template(self.__child_opts, self.__build_middleware)
        self.compose = {}

        for module_path in (Path(__file__).parent / "compose").glob("*.py"):
            name = "{}-compose".format(module_path.stem)
            self.compose[module_path.stem] = self.__compose_file.build(
                module_path=module_path,
                config={
                    "name": name,
                    "volume": _compose_config["volume"],
                    "path": "{}.yaml".format(name),
                },
                input_fn=self.__build_input_fn,
            )

        self.register_outputs({k: v["content"] for k, v in self.compose.items()})

    def __build_input_fn(self, config):
        input_dict = config["input"]

        if "networks" not in input_dict:
            input_dict["networks"] = {}
        input_dict["networks"]["default-bridge"] = {
            "name": default_bridge_network.name,
            "external": True,
        }

        volume_dict = {}

        for cs in input_dict["services"].values():
            if "networks" not in cs and "network_mode" not in cs:
                cs["networks"] = ["default-bridge"]

                for cv in cs.get("volumes").values():
                    if "volume" in cv:
                        volume = cv["volume"]
                        volume_dict[volume] = {
                            "name": docker_volume.volume_map[volume],
                            "external": True,
                        }

        if len(volume_dict):
            input_dict["volumes"] = volume_dict

        return config

    def __build_middleware(self, input, _):
        input["version"] = "3.9"

        for cs in input["services"].values():
            cs["environment"] = {
                k: (json.dumps(v) if isinstance(v, dict) else v).replace("$", "$$")
                for k, v in cs.pop("environment", {}).items()
            }

            volumes = []
            for kv, cv in cs.pop("volumes", {}).items():
                src_path = cv.get("volume", cv.get("host", kv))
                mount_str = "{}:{}:{}".format(
                    src_path, kv, "ro" if cv.get("ro") else "rw"
                )
                volumes.append(mount_str)
            cs["volumes"] = volumes

        return input


docker_compose = DockerCompose()
