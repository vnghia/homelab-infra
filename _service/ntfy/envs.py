import os
from pathlib import Path

from _common import container_storage_config, service_config
from _network.dns import hostnames

_ntfy_config = service_config["ntfy"]
_ntfy_volume = container_storage_config["ntfy"]

NTFY_SMTP_PORT = 25
NTFY_SMTP_DOMAIN = hostnames[_ntfy_config["email-server"]["domain"]]

envs = {
    "NTFY_BASE_URL": "https://{}".format(hostnames["public-ntfy"]),
    "NTFY_CACHE_FILE": os.fspath(Path(_ntfy_volume["cache"]["dir"]) / "cache.db"),
    "NTFY_CACHE_STARTUP_QUERIES": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
    "NTFY_AUTH_FILE": os.fspath(Path(_ntfy_volume["data"]["dir"]) / "user.db"),
    "NTFY_AUTH_DEFAULT_ACCESS": "deny-all",
    "NTFY_AUTH_STARTUP_QUERIES": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
    "NTFY_SMTP_SERVER_LISTEN": ":{}".format(NTFY_SMTP_PORT),
    "NTFY_SMTP_SERVER_DOMAIN": NTFY_SMTP_DOMAIN,
    "NTFY_BEHIND_PROXY": "true",
    "NTFY_ATTACHMENT_CACHE_DIR": os.fspath(
        Path(_ntfy_volume["cache"]["dir"]) / "attachment/"
    ),
    "NTFY_ENABLE_SIGNUP": "false",
    "NTFY_ENABLE_METRICS": "false",
    "NTFY_LOG_LEVEL": "info",
    "NTFY_LOG_FORMAT": "json",
}
