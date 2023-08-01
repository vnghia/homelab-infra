from pathlib import Path

from pulumi import ComponentResource, ResourceOptions
from slugify import slugify

from _common import import_module, service_config
from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_script_server_config = service_config["script-server"]


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

        self.__raw_input = {"name": "__raw_input", "type": "text"}
        self.__import_and_build()

        self.__container = DockerContainer.build(
            "script-server",
            opts=self.__child_opts,
            volumes={"/var/run/docker.sock": {}},
            uploads=[self._config["docker"]]
            + [runner["docker"] for runner in self.__runners.values()]
            + [schedule["docker"] for schedule in self.__schedules.values()],
        )

        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})

    def __build_runner(self, name: str, config: dict):
        path = "{}/{}".format(slugify(config["group"]), slugify(name))
        output_config = {"path": "/app/conf/runners/{}.json".format(path)}

        input_dict = {"name": name} | config
        input_dict["script_path"] = " ".join(input_dict["script_path"])
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
        self.__runners[name] = self.__template.build(config=output_config)

    def __build_schedule(
        self, name: str, path: str, schedule: dict, parameter_values: dict | None
    ):
        output_config = {"path": "/app/conf/schedules/{}.json".format(path)}

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
                "audit_names": {"proxied_ip": _script_server_config["admin"]},
            },
            "script_name": name,
            "schedule": schedule,
            "parameter_values": parameter_values,
        }

        output_config["input"] = input_dict
        self.__schedules[name] = self.__template.build(config=output_config)

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
