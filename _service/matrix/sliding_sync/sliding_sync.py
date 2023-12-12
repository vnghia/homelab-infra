from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.matrix.sliding_sync.envs import envs
from _service.resource import child_opts


class SlidingSync(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:SlidingSync", "sliding-sync", None, child_opts)
        self.__container = DockerContainer.build(
            "sliding-sync",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["sliding-sync"]["file"]],
            ),
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


sliding_sync = SlidingSync()
