from pulumi import Output

from _common import service_config
from _network.dns import hostnames

_docker_browser_config = service_config["docker-browser"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "docker-browser",
            "rule": Output.format("Host(`{0}`)", hostnames["private-docker-browser"]),
        },
        "service": {"port": _docker_browser_config["port"]},
    }
}
