from pulumi import ComponentResource, ResourceOptions

from _common import service_config
from _container import DockerContainer
from _network.resource import child_opts

_cloudflare_config = service_config["cloudflare"]


class Cloudflared(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:proxy:Cloudflared", "cloudflared", None, child_opts)
        self.__container = DockerContainer.build(
            "cloudflared",
            opts=ResourceOptions(parent=self),
            command=["tunnel", "run"],
            envs={"TUNNEL_TOKEN": _cloudflare_config["cloudflared"]["token"]},
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


cloudflared = Cloudflared()
