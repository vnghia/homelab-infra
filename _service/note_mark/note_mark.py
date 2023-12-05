from pulumi import ComponentResource, ResourceOptions

from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.note_mark.envs import envs
from _service.resource import child_opts


class NoteMark(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:NoteMark", "note-mark", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__frontend_container = DockerContainer.build(
            "note-mark-frontend",
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[
                        traefik_proxy.dynamic_config["note-mark-frontend"]["file"]
                    ]
                )
            ),
        )

        self.__backend_container = DockerContainer.build(
            "note-mark-backend",
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[
                        traefik_proxy.dynamic_config["note-mark-backend"]["file"]
                    ]
                )
            ),
            envs=envs,
        )

        self.frontend_container_id = self.__frontend_container.id
        self.backend_container_id = self.__backend_container.id
        self.register_outputs(
            {
                "frontend_container_id": self.frontend_container_id,
                "backend_container_id": self.backend_container_id,
            }
        )


note_mark = NoteMark()
