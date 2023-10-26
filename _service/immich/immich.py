from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.immich.envs import envs, typesense_envs
from _service.resource import child_opts


class Immich(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Immich", "immich", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__server_container = DockerContainer.build(
            "immich-server",
            opts=self.__child_opts,
            command=["start.sh", "immich"],
            envs=envs,
        )
        self.__microservices_container = DockerContainer.build(
            "immich-microservices",
            opts=self.__child_opts,
            image="immich-server",
            command=["start.sh", "microservices"],
            envs=envs,
        )
        self.__machine_learning_container = DockerContainer.build(
            "immich-machine-learning", opts=self.__child_opts, envs=envs
        )
        self.__web_container = DockerContainer.build(
            "immich-web", opts=self.__child_opts, envs=envs
        )
        self.__typesense_container = DockerContainer.build(
            "immich-typesense", opts=self.__child_opts, envs=typesense_envs
        )

        self.server_container_id = self.__server_container.id
        self.microservices_container_id = self.__microservices_container.id
        self.machine_learning_container_id = self.__machine_learning_container.id
        self.web_container_id = self.__web_container.id
        self.typesense_container_id = self.__typesense_container.id
        self.register_outputs(
            {
                "server_container_id": self.server_container_id,
                "microservices_container_id": self.microservices_container_id,
                "machine_learning_container_id": self.machine_learning_container_id,
                "web_container_id": self.web_container_id,
                "typesense_container_id": self.typesense_container_id,
            }
        )


immich = Immich()
