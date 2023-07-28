from _common import ntfy_config
from _network.dns import hostnames

output_config = {
    "type": "yaml",
    "name": "ntfy-server-config",
    "volume": ntfy_config["volume"]["config"]["volume"],
    "path": "server.yml",
    "input": {
        "base-url": "https://{}".format(hostnames["public-ntfy"]),
        "cache-file": "{}cache.db".format(ntfy_config["volume"]["cache"]["volume"]),
        "cache-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "auth-file": "{}user.db".format(ntfy_config["volume"]["data"]["volume"]),
        "auth-default-access": "deny-all",
        "auth-startup-queries": "pragma journal_mode = WAL;\npragma synchronous = normal;\npragma temp_store = memory;\npragma busy_timeout = 15000;\nvacuum;\n",
        "behind-proxy": True,
        "attachment-cache-dir": "{}attachment/".format(
            ntfy_config["volume"]["cache"]["volume"]
        ),
        "enable-signup": False,
        "enable-metrics": False,
        "log-level": "info",
        "log-format": "json",
    },
}
