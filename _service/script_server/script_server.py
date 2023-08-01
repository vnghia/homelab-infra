from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _service.resource import child_opts


class ScriptServer(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "service:index:ScriptServer", "script-server", None, child_opts
        )
        self.__child_opts = ResourceOptions(
            parent=self,
            depends_on=[traefik_proxy.dynamic_config["script-server"]["file"]],
        )

        self._config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "config.py"
        )
        self.__container = DockerContainer.build(
            "script-server",
            opts=self.__child_opts,
            uploads=[self._config["docker"]],
        )

        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


script_server = ScriptServer()
