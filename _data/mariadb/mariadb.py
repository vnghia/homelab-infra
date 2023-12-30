from pulumi import ComponentResource, Output, ResourceOptions

from _common import mariadb_config
from _container import DockerContainer
from _data.resource import child_opts
from _secret import secret


class MariaDB(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:mariadb:MariaDB", "mariadb", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.db: dict = {}
        self.port = 3306

        for db, _ in mariadb_config.items():
            name = "mariadb-{}".format(db)
            password = secret.keys["mariadb-{}".format(db)].result

            DockerContainer.build(
                name,
                opts=self.__child_opts,
                image="mariadb",
                envs={
                    "MARIADB_ROOT_PASSWORD": password,
                    "MARIADB_DATABASE": db,
                },
            )

            self.db[db] = {
                "host": name,
                "port": self.port,
                "username": "root",
                "password": password,
                "database": db,
                "url": Output.format(
                    "mysql://root:{0}@{1}:{2}/{3}", password, name, self.port, db
                ),
            }

        self.register_outputs({})


mariadb = MariaDB()
