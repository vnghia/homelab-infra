from pulumi import Output

from _common import service_config
from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "immich-web",
            "rule": Output.format("Host(`{0}`)", hostnames["private-immich"]),
        },
        "service": {"port": 3000},
    }
}
