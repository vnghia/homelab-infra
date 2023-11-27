from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _data.docker_browser.envs import envs
from _data.resource import child_opts
from _network.traefik import traefik_proxy


class DockerBrowser(ComponentResource):
    def __init__(self) -> None:
        super().__init__(
            "data:docker:DockerBrowser", "docker-browser", None, child_opts
        )
        self.__container = DockerContainer.build(
            "docker-browser",
            opts=ResourceOptions(
                parent=self,
                depends_on=[traefik_proxy.dynamic_config["docker-browser"]["file"]],
            ),
            image="dufs",
            envs=envs,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


docker_browser = DockerBrowser()
