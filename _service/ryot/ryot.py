from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts
from _service.ryot.envs import envs


class Ryot(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Ryot", "ryot", None, child_opts)
        self.__container = DockerContainer.build(
            "ryot",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["ryot"]["file"]],
            ),
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


ryot = Ryot()
