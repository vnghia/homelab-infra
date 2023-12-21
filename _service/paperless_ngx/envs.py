from pulumi import Output

from _common import server_config
from _data.redis import redis
from _network.dns import hostnames
from _secret import secret

_redis_config = redis.db["paperless-ngx"]
_account_config = secret.accounts["paperless-ngx"]

envs = {
    "PAPERLESS_REDIS": Output.format(
        "redis://{0}:{1}@{2}:{3}",
        _redis_config["username"],
        _redis_config["password"],
        _redis_config["host"],
        _redis_config["port"],
    ),
    "PAPERLESS_SECRET_KEY": secret.keys["paperless-ngx-secret"].result,
    "PAPERLESS_URL": "https://{}".format(hostnames["private-paperless-ngx"]),
    "PAPERLESS_AUTO_LOGIN_USERNAME": _account_config["username"],
    "PAPERLESS_ADMIN_USER": _account_config["username"],
    "PAPERLESS_ADMIN_PASSWORD": _account_config["password"],
    "PAPERLESS_FILENAME_FORMAT": "{document_type}/{correspondent}/{created_year}/{tag_list}/{title}",
    "PAPERLESS_FILENAME_FORMAT_REMOVE_NONE": "True",
    "PAPERLESS_CONSUMER_POLLING": "0",
    "PAPERLESS_TIME_ZONE": server_config["tz"],
}
