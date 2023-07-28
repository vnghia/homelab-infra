from _common import container_storage_config
from _network.dns import hostnames

_ntfy_volume = container_storage_config["ntfy"]

output_config = {
    "type": "yaml",
    "name": "ntfy-server-config",
    "volume": _ntfy_volume["config"]["volume"],
    "path": "server.yml",
    "input": {
        "base-url": "https://{}".format(hostnames["public-ntfy"]),
        "cache-file": "{}cache.db".format(_ntfy_volume["cache"]["volume"]),
        "cache-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "auth-file": "{}user.db".format(_ntfy_volume["data"]["volume"]),
        "auth-default-access": "deny-all",
        "auth-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "behind-proxy": True,
        "attachment-cache-dir": "{}attachment/".format(_ntfy_volume["cache"]["volume"]),
        "enable-signup": False,
        "enable-metrics": False,
        "log-level": "info",
        "log-format": "json",
    },
}
