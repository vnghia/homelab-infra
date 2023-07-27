from pulumi import ComponentResource, Output, ResourceOptions

from _common import syncthing_config
from _container import DockerContainer
from _network.tailscale import tailscale_device
from _service.resource import child_opts


class Syncthing(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Syncthing", "syncthing", None, child_opts)
        self.__container = DockerContainer.build(
            "syncthing",
            opts=ResourceOptions(parent=self),
            network_mode=Output.concat("container:", tailscale_device.container_id),
            volume_config=syncthing_config["volume"],
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


syncthing = Syncthing()
