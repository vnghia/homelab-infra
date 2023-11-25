from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import get_logical_name, service_config
from _container import DockerContainer
from _file import Template
from _network.resource import child_opts
from _secret import secret

_crowdsec_config = service_config["crowdsec"]


# TODO: Connection Central API does not work in bridge network.
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

        self.bouncer_key = secret.build_string("traefik-bouncer-key", length=32).result

        self.__container = DockerContainer.build(
            "crowdsec",
            opts=self.__child_opts,
            envs={
                "COLLECTIONS": " ".join(
                    ["crowdsecurity/traefik", "LePresidente/authelia"]
                ),
                "CUSTOM_HOSTNAME": "crowdsec",
                "ENROLL_KEY": _crowdsec_config["console-id"],
                "ENROLL_INSTANCE_NAME": get_logical_name(),
                "USE_WAL": "true",
                "BOUNCER_KEY_TRAEFIK": self.bouncer_key,
            },
            volumes={"/var/run/docker.sock": {"ro": True}},
            labels={
                "acquis-traefik-sha256": self.__acquis_traefik["sha256"],
                "acquis-authelia-sha256": self.__acquis_authelia["sha256"],
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


crowdsec = Crowdsec()
