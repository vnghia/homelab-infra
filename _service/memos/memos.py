from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.memos.envs import envs
from _service.resource import child_opts


class Memos(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Memos", "memos", None, child_opts)
        self.__container = DockerContainer.build(
            "memos",
            opts=ResourceOptions(
                parent=self, depends_on=[traefik_proxy.dynamic_config["memos"]["file"]]
            ),
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


memos = Memos()
