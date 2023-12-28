from pulumi import Output

from _common import service_config
from _network.dns import hostnames
from _network.vpn.vpn import vpn

_qbittorrent_config = service_config["qbittorrent"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "qbittorrent",
            "rule": Output.format("Host(`{0}`)", hostnames["private-qbittorrent"]),
        },
        "service": {
            "host": vpn.networks["default"]["host"],
            "port": _qbittorrent_config["port"],
        },
    }
}
