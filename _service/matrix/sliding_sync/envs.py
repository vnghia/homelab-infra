from pulumi import Output

from _data.postgres import postgres
from _secret import secret

_postgres_config = postgres.db["sliding-sync"]

envs = {
    "SYNCV3_SERVER": "http://dendrite:8008",
    "SYNCV3_DB": Output.format(
        "postgresql://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
        _postgres_config["username"],
        _postgres_config["password"],
        _postgres_config["host"],
        _postgres_config["port"],
        _postgres_config["database"],
    ),
    "SYNCV3_SECRET": secret.keys["sliding-sync-encryption"].result,
}
