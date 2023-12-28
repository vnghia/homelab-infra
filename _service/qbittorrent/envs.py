from _common import service_config

_qbittorrent_config = service_config["qbittorrent"]

envs = {"QBT_EULA": "accept", "QBT_WEBUI_PORT": _qbittorrent_config["port"]}
