from pulumi import ComponentResource, Output, ResourceOptions

from _common import service_config
from _container import DockerContainer
from _secret import secret
from _service.resource import child_opts

meilisearch_config = service_config["meilisearch"]


class MeiliSearch(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:MeiliSearch", "meilisearch", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__master_key = secret.build_password(
            "meilisearch-master-key", opts=self.__child_opts, length=32, special=False
        ).result

        self.__container = DockerContainer.build(
            "meilisearch",
            opts=self.__child_opts,
            envs={
                "MEILI_ENV": "production",
                "MEILI_MASTER_KEY": self.__master_key,
                "MEILI_HTTP_ADDR": "0.0.0.0:{}".format(meilisearch_config["port"]),
            },
        )

        self.env = {
            "MEILISEARCH_HOST": Output.format(
                "http://{}:{}", self.__container.name, meilisearch_config["port"]
            ),
            "MEILISEARCH_KEY": self.__master_key,
        }

        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


meilisearch = MeiliSearch()
