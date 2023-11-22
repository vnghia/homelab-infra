import os
from pathlib import Path

from _common import container_storage_config, service_config
from _network.dns import hostnames

_ntfy_config = service_config["ntfy"]
_ntfy_volume = container_storage_config["ntfy"]

NTFY_SMTP_PORT = 25
NTFY_SMTP_DOMAIN = hostnames[_ntfy_config["email-server"]["domain"]]

output_config = {
    "type": "yaml",
    "name": "ntfy-server-config",
    "volume": _ntfy_volume["config"]["volume"],
    "path": "server.yml",
    "input": {
        "base-url": "https://{}".format(hostnames["public-ntfy"]),
        "cache-file": os.fspath(Path(_ntfy_volume["cache"]["dir"]) / "cache.db"),
        "cache-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "auth-file": os.fspath(Path(_ntfy_volume["data"]["dir"]) / "user.db"),
        "auth-default-access": "deny-all",
        "auth-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "smtp-server-listen": ":{}".format(NTFY_SMTP_PORT),
        "smtp-server-domain": NTFY_SMTP_DOMAIN,
        "behind-proxy": True,
        "attachment-cache-dir": "{}attachment/".format(_ntfy_volume["cache"]["volume"]),
        "enable-signup": False,
        "enable-metrics": False,
        "log-level": "info",
        "log-format": "json",
    },
}
