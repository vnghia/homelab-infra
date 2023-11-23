from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _service.resource import child_opts


class Authelia(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Authelia", "authelia", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__template = Template(self.__child_opts)

        self.__configuration = self.__template.build(
            module_path=Path(__file__).parent / "configuration.py"
        )
        self.__users = self.__template.build(
            module_path=Path(__file__).parent / "users.py"
        )

        self.__container = DockerContainer.build(
            "authelia",
            opts=self.__child_opts,
            labels={
                "configuration-sha256": self.__configuration["sha256"],
                "users-sha256": self.__users["sha256"],
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


authelia = Authelia()
