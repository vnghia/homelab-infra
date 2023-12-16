from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.immich.envs import envs
from _service.resource import child_opts


class Immich(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Immich", "immich", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__server_container = DockerContainer.build(
            "immich-server",
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[traefik_proxy.dynamic_config["immich"]["file"]]
                )
            ),
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
            "immich-machine-learning",
            opts=self.__child_opts,
            envs=envs | {"MACHINE_LEARNING_MODEL_TTL": 3600},
        )

        self.server_container_id = self.__server_container.id
        self.microservices_container_id = self.__microservices_container.id
        self.machine_learning_container_id = self.__machine_learning_container.id
        self.register_outputs(
            {
                "server_container_id": self.server_container_id,
                "microservices_container_id": self.microservices_container_id,
                "machine_learning_container_id": self.machine_learning_container_id,
            }
        )


immich = Immich()
