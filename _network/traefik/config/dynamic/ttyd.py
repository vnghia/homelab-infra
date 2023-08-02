from pulumi import Output

from _common import service_config
from _network.dns import hostnames

_ttyd_config = service_config["ttyd"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "ttyd",
            "rule": Output.format(
                "Host(`{0}`) && PathPrefix(`{1}`)",
                hostnames["private-infra"],
                _ttyd_config["base-path"],
            ),
        },
        "service": {"port": _ttyd_config["port"]},
    }
}
