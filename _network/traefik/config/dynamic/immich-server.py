from pulumi import Output

from _common import service_config
from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "immich-server",
            "rule": Output.format(
                "Host(`{0}`) && PathPrefix(`/api`)", hostnames["private-immich"]
            ),
            "middlewares": ["immich-api-strip-prefix"],
        },
        "service": {"port": 3001},
        "middleware": {
            "immich-api-strip-prefix": {"name": "stripPrefix", "prefixes": ["/api"]}
        },
    }
}
