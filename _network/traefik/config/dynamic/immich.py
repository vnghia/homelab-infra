from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "immich-server",
            "rule": Output.format("Host(`{0}`)", hostnames["private-immich"]),
        },
        "service": {"port": 3001},
    }
}
