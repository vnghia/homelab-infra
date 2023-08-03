from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _common import redis_config
from _container import DockerContainer
from _data.resource import child_opts
from _file import Template
from _secret import secret


class Redis(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:redis:Redis", "Redis", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        config_path = Path(__file__).parent / "conf.py"

        self.db: dict = {}
        self.port = 6379

        self.__template = Template(self.__child_opts)

        for db in redis_config:
            name = "redis-{}".format(db)
            password = secret.build_password(
                name, opts=self.__child_opts, length=8, special=False
            ).result
            redis_conf = self.__template.build(
                module_path=config_path,
                input_args={"port": self.port, "password": password},
            )
            DockerContainer.build(
                name,
                opts=self.__child_opts,
                command=["redis-server", redis_conf["config"]["path"]],
                image="redis",
                uploads=[redis_conf["docker"]],
            )

            self.db[db] = {
                "host": name,
                "port": self.port,
                "username": "default",
                "password": password,
            }

        self.register_outputs({})


redis = Redis()
