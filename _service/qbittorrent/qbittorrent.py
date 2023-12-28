from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _network.vpn.vpn import vpn
from _service.qbittorrent.envs import envs
from _service.resource import child_opts


class Qbittorrent(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Qbittorrent", "qbittorrent", None, child_opts)
        self.__container = DockerContainer.build(
            "qbittorrent",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["qbittorrent"]["file"]],
            ),
            network_mode=vpn.networks["default"]["network"],
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


qbittorrent = Qbittorrent()
