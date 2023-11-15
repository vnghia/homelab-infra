from pulumi import ComponentResource, ResourceOptions

from _common import postgres_config
from _container import DockerContainer
from _data.resource import child_opts
from _secret import secret


class Postgres(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:postgres:Postgres", "Postgres", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.db: dict = {}
        self.port = 5432

        for db, _ in postgres_config.items():
            name = "postgres-{}".format(db)
            password = secret.build_password(
                name, opts=self.__child_opts, length=32, special=False
            ).result

            DockerContainer.build(
                name,
                opts=self.__child_opts,
                image="postgres",
                envs={
                    "POSTGRES_PASSWORD": password,
                    "POSTGRES_USER": db,
                    "POSTGRES_DB": db,
                    "PGDATA": "/var/lib/postgresql/data/",
                },
            )

            self.db[db] = {
                "host": name,
                "port": self.port,
                "username": db,
                "password": password,
                "database": db,
            }

        self.register_outputs({})


postgres = Postgres()
