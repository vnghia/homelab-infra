from pulumi import ComponentResource, ResourceOptions
from pulumi_docker import ContainerPortArgs

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts
from _service.slskd.envs import envs


class Slskd(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Slskd", "slskd", None, child_opts)
        self.__listen_port = envs["SLSKD_SLSK_LISTEN_PORT"]
        self.__container = DockerContainer.build(
            "slskd",
            opts=ResourceOptions(
                parent=self, depends_on=[traefik_proxy.dynamic_config["slskd"]["file"]]
            ),
            envs=envs,
            ports=[
                ContainerPortArgs(
                    internal=self.__listen_port, external=self.__listen_port
                )
            ],
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


slskd = Slskd()
