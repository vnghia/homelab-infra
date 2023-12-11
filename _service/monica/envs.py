from _common import service_config
from _data.postgres import postgres
from _data.redis import redis
from _network.dns.hostnames import hostnames
from _secret import secret

_monica_config = service_config["monica"]
_ntfy_config = service_config["ntfy"]

_redis_config = redis.db["monica"]
_postgres_config = postgres.db["monica"]

envs = {
    "APP_NAME": "Libra",
    "APP_ENV": "production",
    "APP_KEY": secret.keys["monica-app"].result,
    "APP_DEBUG": False,
    "APP_URL": hostnames["private-monica"],
    "DB_CONNECTION": "pgsql",
    "DB_HOST": _postgres_config["host"],
    "DB_PORT": _postgres_config["port"],
    "DB_USERNAME": _postgres_config["username"],
    "DB_PASSWORD": _postgres_config["password"],
    "DB_DATABASE": _postgres_config["database"],
    "APP_TRUSTED_PROXIES": "*",
    "CACHE_DRIVER": "redis",
    # TODO: Set to `redis` when this issue is fixed.
    # https://github.com/monicahq/monica/issues/7039
    "QUEUE_CONNECTION": "sync",
    "SESSION_DRIVER": "redis",
    "DEFAULT_STORAGE_LIMIT": 0,
    "REDIS_HOST": _redis_config["host"],
    "REDIS_PORT": _redis_config["port"],
    "REDIS_PASSWORD": _redis_config["password"],
    "UPLOADCARE_PUBLIC_KEY": _monica_config["uploadcare"]["public-key"],
    "UPLOADCARE_PRIVATE_KEY": _monica_config["uploadcare"]["private-key"],
    "LOCATION_IQ_API_KEY": _monica_config["location-iq-api-key"],
    "MAPBOX_API_KEY": _monica_config["mapbox"]["api-key"],
    "MAPBOX_USERNAME": _monica_config["mapbox"]["username"],
    "MAIL_MAILER": "smtp",
    "MAIL_HOST": hostnames["private-mailserver"],
    "MAIL_PORT": 25,
    "MAIL_FROM_ADDRESS": "notification@{}".format(
        hostnames[_ntfy_config["email-server"]["service"]["monica"]]
    ),
}
