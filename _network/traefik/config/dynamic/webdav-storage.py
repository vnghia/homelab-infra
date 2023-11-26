from pulumi import Output

from _common import service_config
from _network.dns import hostnames

_webdav_storage_config = service_config["webdav-storage"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "webdav-storage",
            "rule": Output.format("Host(`{0}`)", hostnames["private-webdav-storage"]),
        },
        "service": {"port": _webdav_storage_config["port"]},
    }
}
