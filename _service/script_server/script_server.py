import os
from pathlib import Path

from pulumi import ComponentResource, Output, ResourceOptions
from slugify import slugify

from _common import container_storage_config, import_module, service_config
from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_script_server_config = service_config["script-server"]
_script_server_volume = container_storage_config["script-server"]


class ScriptServer(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "service:index:ScriptServer", "script-server", None, child_opts
        )
        self.__child_opts = ResourceOptions(
            parent=self,
            depends_on=[traefik_proxy.dynamic_config["script-server"]["file"]],
        )

        self.__template = Template(self.__child_opts)

        self._config = self.__template.build(
            module_path=Path(__file__).parent / "config.py"
        )

        self.__runners: dict[str, Template] = {}
        self.__schedules: dict[str, Template] = {}
        self.__scripts: dict[str, Template] = {}

        self.__raw_input = {"name": "__raw_input", "type": "text"}
        self.__import_and_build()

        self.__container = DockerContainer.build(
            "script-server",
            opts=self.__child_opts,
            command=[
                "-f",
                os.fspath(
                    Path(_script_server_volume["config-only"]["dir"])
                    / self._config["config"]["path"]
                ),
            ],
            volumes={"/var/run/docker.sock": {}},
            labels={"config-sha256": self._config["sha256"]}
            | {
                "runner-{}-sha256".format(k.removeprefix("script-server-")): v["sha256"]
                for k, v in self.__runners.items()
            }
            | {
                "schedule-{}-sha256".format(k.removeprefix("script-server-")): v[
                    "sha256"
                ]
                for k, v in self.__schedules.items()
            }
            | {
                "script-{}-sha256".format(k.removeprefix("script-server-")): v["sha256"]
                for k, v in self.__scripts.items()
            },
        )

        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})

    def __build_runner(self, name: str, config: dict):
        slugify_name = slugify(name)

        path = os.fspath(Path(slugify(config["group"])) / slugify_name)
        output_config = {
            "name": "script-server-runner-{}".format(slugify_name),
            "volume": _script_server_volume["runners"]["volume"],
            "path": "{}.json".format(path),
        }

        input_dict = {"name": name} | config
        script_type_map = {
            "shell": self.__build_script_shell,
            None: lambda _1, _2, scripts: Output.from_input(scripts).apply(
                lambda scripts: " ".join(scripts)
            ),
        }
        input_dict["script_path"] = script_type_map[config.get("script_type")](
            name, path, input_dict["script_path"]
        )

        if "parameters" not in input_dict:
            input_dict["parameters"] = []
        input_dict["parameters"].append(self.__raw_input)

        if "scheduling" in input_dict:
            cs = input_dict.pop("scheduling")
            input_dict["scheduling"] = {"enabled": True}

            self.__build_schedule(
                name,
                path.replace("/", "-"),
                cs["schedule"],
                cs.get("parameter_values"),
            )

        output_config["input"] = input_dict
        self.__runners[slugify_name] = self.__template.build(config=output_config)

    def __build_schedule(
        self, name: str, path: str, schedule: dict, parameter_values: dict | None
    ):
        slugify_name = slugify(name)

        output_config = {
            "name": "script-server-schedule-{}".format(slugify_name),
            "volume": _script_server_volume["schedules"]["volume"],
            "path": "{}.json".format(path),
        }

        schedule["repeatable"] = schedule.pop("repeatable", True)
        schedule["executions_count"] = schedule.pop("executions_count", 0)
        schedule["start_datetime"] = schedule["start_datetime"].strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        parameter_values = parameter_values or {}
        parameter_values["__raw_input"] = ""

        input_dict = {
            "id": len(self.__schedules) + 1,
            "user": {
                "user_id": _script_server_config["admin"],
                "audit_names": {"auth_username": _script_server_config["admin"]},
            },
            "script_name": name,
            "schedule": schedule,
            "parameter_values": parameter_values,
        }

        output_config["input"] = input_dict
        self.__schedules[slugify_name] = self.__template.build(config=output_config)

    def __build_script_shell(self, name: str, path: str, scripts: list[list]):
        slugify_name = slugify(name)

        script_path = "{}.sh".format(path)
        full_path = os.fspath(
            Path(_script_server_volume["scripts"]["dir"]) / script_path
        )

        output_config = {
            "name": "script-server-script-{}".format(slugify_name),
            "volume": _script_server_volume["scripts"]["volume"],
            "path": script_path,
            "type": "raw",
        }

        output_config["input"] = Output.from_input(scripts).apply(
            lambda scripts: "\n".join(
                ["#!/bin/sh", "", "set -euxo pipefail", ""]
                + [" ".join(script) for script in scripts]
                + [""]
            )
        )
        self.__scripts[slugify_name] = self.__template.build(config=output_config)
        return full_path

    def __import_and_build(self):
        for path in sorted(
            (Path(__file__).parent / "runners").glob("*.py"),
            key=lambda x: x.name,
        ):
            module = import_module(path)
            for script, config in module.script_config.items():
                self.__build_runner(
                    script,
                    module.common_config | config,
                )


script_server = ScriptServer()
