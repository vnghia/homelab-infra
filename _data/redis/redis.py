from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, Output, ResourceOptions

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
            password = secret.keys["redis-{}".format(db)].result
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
                healthcheck=docker.ContainerHealthcheckArgs(
                    tests=[
                        "CMD",
                        "redis-cli",
                        "-a",
                        password,
                        "--raw",
                        "incr",
                        "ping",
                    ],
                    interval="5s",
                    timeout="5s",
                    retries=5,
                ),
            )

            self.db[db] = {
                "host": name,
                "port": self.port,
                "username": "default",
                "password": password,
                "url": Output.format(
                    "redis://default:{0}@{1}:{2}/0", password, name, self.port
                ),
            }

        self.register_outputs({})


redis = Redis()
