from _data.postgres import postgres
from _secret import secret

_postgres_config = postgres.db["sliding-sync"]

envs = {
    "SYNCV3_SERVER": "http://dendrite:8008",
    "SYNCV3_DB": _postgres_config["url"],
    "SYNCV3_SECRET": secret.keys["sliding-sync-encryption"].result,
}
