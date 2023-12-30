import pulumi_docker as docker
from pulumi import ComponentResource, Output, ResourceOptions

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

        for db, config in postgres_config.items():
            name = "postgres-{}".format(db)
            password = secret.keys["postgres-{}".format(db)].result

            config = config or {}

            DockerContainer.build(
                name,
                opts=self.__child_opts,
                image=config.pop("image", "postgres"),
                envs={
                    "POSTGRES_PASSWORD": password,
                    "POSTGRES_USER": db,
                    "POSTGRES_DB": db,
                    "PGDATA": "/var/lib/postgresql/data/",
                },
                healthcheck=docker.ContainerHealthcheckArgs(
                    tests=["CMD", "pg_isready", "-U", db],
                    interval="5s",
                    timeout="5s",
                    retries=5,
                ),
                wait=True,
            )

            self.db[db] = {
                "host": name,
                "port": self.port,
                "username": db,
                "password": password,
                "database": db,
                "url": Output.format(
                    "postgresql://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
                    db,
                    password,
                    name,
                    self.port,
                    db,
                ),
                "url-pgsql": Output.format(
                    "pgsql://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
                    db,
                    password,
                    name,
                    self.port,
                    db,
                ),
            }

        self.register_outputs({})


postgres = Postgres()
