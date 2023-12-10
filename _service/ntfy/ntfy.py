from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, Output, ResourceOptions

from _command import Command
from _container import DockerContainer
from _network.traefik import traefik_proxy
from _secret import secret
from _service.ntfy.envs import NTFY_SMTP_DOMAIN, NTFY_SMTP_PORT, envs
from _service.resource import child_opts


class Ntfy(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Ntfy", "ntfy", None, child_opts)
        self.__child_opts = ResourceOptions(
            parent=self, depends_on=[traefik_proxy.dynamic_config["ntfy"]["file"]]
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
            envs=envs,
            wait=True,
        )

        self.container_id = self.__container.id

        self.__access = Command.build(
            "ntfy-access-setup",
            opts=self.__child_opts,
            create=Path(__file__).parent / "add_access.py",
            delete=Path(__file__).parent / "delete_access.py",
            update="import os;print(os.environ['PULUMI_COMMAND_STDOUT'])",
            environment={
                "NTFY_CONTAINER_ID": self.container_id,
                "NTFY_USERNAME": secret.accounts["ntfy"]["username"],
                "NTFY_PASSWORD": secret.accounts["ntfy"]["password"],
                "NTFY_WRITE_ONLY_USERNAME": secret.accounts["ntfy-write-only"][
                    "username"
                ],
                "NTFY_WRITE_ONLY_PASSWORD": secret.accounts["ntfy-write-only"][
                    "password"
                ],
            },
        )

        self.env = {
            "NTFY_ENDPOINT": Output.format("http://{}:80", self.__container.name),
            "NTFY_TOKEN": self.__access.stdout,
        }

        self.smtp_env = {
            "NTFY_SMTP_SERVER": self.__container.name,
            "NTFY_SMTP_PORT": NTFY_SMTP_PORT,
            "NTFY_TOKEN": self.__access.stdout,
        }

        self.register_outputs({"container_id": self.container_id})

    def build_to_email(self, topic: str):
        return Output.format(
            "{0}+{1}@{2}", topic, self.__access.stdout, NTFY_SMTP_DOMAIN
        )


ntfy = Ntfy()
