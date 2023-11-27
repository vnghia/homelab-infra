from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _service.mailserver.envs import envs
from _service.resource import child_opts


class Mailserver(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Mailserver", "mailserver", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__template = Template(self.__child_opts)

        self.__postfix_main = self.__template.build(
            module_path=Path(__file__).parent / "postfix-main.py"
        )
        self.__postfix_regexp = self.__template.build(
            module_path=Path(__file__).parent / "postfix-regexp.py"
        )

        self.__container = DockerContainer.build(
            "mailserver",
            opts=self.__child_opts,
            envs=envs,
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=[
                    "CMD-SHELL",
                    "ss --listening --tcp | grep -P 'LISTEN.+:smtp' || exit 1",
                ],
                timeout="3s",
                retries=0,
            ),
            labels={
                "postfix-main-sha256": self.__postfix_main["sha256"],
                "postfix-regexp-sha256": self.__postfix_regexp["sha256"],
            },
            network_aliases=[envs["OVERRIDE_HOSTNAME"]],
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


mailserver = Mailserver()
