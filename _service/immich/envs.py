from _common import container_storage_config
from _data.postgres import postgres
from _data.redis import redis
from _network.dns import hostnames
from _secret import secret

_redis_config = redis.db["immich"]
_postgres_config = postgres.db["immich"]
_immich_typesense_volume = container_storage_config["immich-typesense"]

envs = {
    "PUBLIC_IMMICH_SERVER_URL": "https://{}".format(hostnames["private-immich"]),
    "DB_HOSTNAME": _postgres_config["host"],
    "DB_PORT": _postgres_config["port"],
    "DB_USERNAME": _postgres_config["username"],
    "DB_PASSWORD": _postgres_config["password"],
    "DB_DATABASE_NAME": _postgres_config["database"],
    "REDIS_HOSTNAME": _redis_config["host"],
    "REDIS_PORT": _redis_config["port"],
    "REDIS_USERNAME": _redis_config["username"],
    "REDIS_PASSWORD": _redis_config["password"],
    "TYPESENSE_API_KEY": secret.build_string("typesense-api-key", length=32).result,
    "TYPESENSE_HOST": "immich-typesense",
}

typesense_envs = {
    "TYPESENSE_API_KEY": envs["TYPESENSE_API_KEY"],
    "TYPESENSE_DATA_DIR": _immich_typesense_volume["data"]["dir"],
}
