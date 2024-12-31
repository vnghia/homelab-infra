from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _file import Template
from _network.resource import child_opts
from _network.security.crowdsec.envs import envs


class Crowdsec(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:security:Crowdsec", "crowdsec", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__template = Template(self.__child_opts)
        self.__acquis_traefik = self.__template.build(
            module_path=Path(__file__).parent / "acquis" / "traefik.py"
        )
        self.__acquis_authelia = self.__template.build(
            module_path=Path(__file__).parent / "acquis" / "authelia.py"
        )
        self.__container = DockerContainer.build(
            "crowdsec",
            opts=self.__child_opts,
            envs=envs,
            volumes={"/var/run/docker.sock": {"ro": True}},
            labels={
                "acquis-traefik-sha256": self.__acquis_traefik["sha256"],
                "acquis-authelia-sha256": self.__acquis_authelia["sha256"],
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


crowdsec = Crowdsec()
