from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _command import Command
from _container import DockerContainer
from _file import Template
from _network.traefik import traefik_proxy
from _secret import secret
from _service.resource import child_opts


class Ntfy(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Ntfy", "ntfy", None, child_opts)
        self.__child_opts = ResourceOptions(
            parent=self, depends_on=[traefik_proxy.dynamic_config["ntfy"]["file"]]
        )

        self.__ntfy_config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "server.py"
        )
        self.__container = DockerContainer.build(
            "ntfy",
            opts=self.__child_opts,
            command=["serve"],
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=[
                    "CMD-SHELL",
                    "wget -q --tries=1 http://localhost:80/v1/health -O - | grep -Eo '\"healthy\"\\s*:\\s*true' || exit 1",
                ],
                interval="1s",
                timeout="5s",
                retries=60,
                start_period="10s",
            ),
            wait=True,
            labels={"ntfy-server-config-sha256": self.__ntfy_config["sha256"]},
        )

        self.container_id = self.__container.id
        self.__access = Command.build(
            "ntfy-access-setup",
            opts=self.__child_opts,
            create=Path(__file__).parent / "add_access.py",
            delete=Path(__file__).parent / "delete_access.py",
            update="",
            environment={
                "NTFY_CONTAINER_ID": self.container_id,
                "NTFY_USERNAME": secret.accounts["ntfy"]["username"],
                "NTFY_PASSWORD": secret.accounts["ntfy"]["password"],
            },
        )

        self.register_outputs({"container_id": self.container_id})


ntfy = Ntfy()
