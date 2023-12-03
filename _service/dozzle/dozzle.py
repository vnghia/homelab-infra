from pulumi import ComponentResource, ResourceOptions

from _common import constant
from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts


class Dozzle(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Dozzle", "dozzle", None, child_opts)
        self.__container = DockerContainer.build(
            "dozzle",
            opts=ResourceOptions(
                parent=self, depends_on=[traefik_proxy.dynamic_config["dozzle"]["file"]]
            ),
            envs={
                "DOZZLE_BASE": "/log",
                "DOZZLE_FILTER": "label=pulumi.stack={}".format(constant.PROJECT_STACK),
                "DOZZLE_ENABLE_ACTIONS": True,
            },
            volumes={"/var/run/docker.sock": {}},
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


dozzle = Dozzle()
