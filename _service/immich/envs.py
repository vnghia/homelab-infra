from _data.postgres import postgres
from _data.redis import redis
from _network.dns import hostnames

_redis_config = redis.db["immich"]
_postgres_config = postgres.db["immich"]

envs = {
    "PUBLIC_IMMICH_SERVER_URL": "https://{}".format(hostnames["private-immich"]),
    "DB_URL": _postgres_config["url"],
    "REDIS_HOSTNAME": _redis_config["host"],
    "REDIS_PORT": _redis_config["port"],
    "REDIS_USERNAME": _redis_config["username"],
    "REDIS_PASSWORD": _redis_config["password"],
}
