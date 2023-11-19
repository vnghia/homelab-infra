from pulumi import ComponentResource, Output, ResourceOptions

from _container import DockerContainer
from _data.postgres import postgres
from _network.dns.hostnames import hostnames
from _network.traefik import traefik_proxy
from _secret import secret
from _service.resource import child_opts

_postgres_config = postgres.db["linkwarden"]


class Linkwarden(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Linkwarden", "linkwarden", None, child_opts)
        self.__container = DockerContainer.build(
            "linkwarden",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["linkwarden"]["file"]],
            ),
            envs={
                "NEXTAUTH_SECRET": secret.build_string(
                    "linkwarden-secret", length=32
                ).result,
                "DATABASE_URL": Output.format(
                    "postgresql://{0}:{1}@{2}:{3}/{4}",
                    _postgres_config["username"],
                    _postgres_config["password"],
                    _postgres_config["host"],
                    _postgres_config["port"],
                    _postgres_config["database"],
                ),
                "NEXTAUTH_URL": "https://{}".format(hostnames["private-linkwarden"]),
                "NEXT_PUBLIC_DISABLE_REGISTRATION": True,
            },
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


linkwarden = Linkwarden()
