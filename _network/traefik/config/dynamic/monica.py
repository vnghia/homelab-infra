from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "monica",
            "rule": Output.format("Host(`{0}`)", hostnames["private-monica"]),
        },
        "service": {"port": 80},
    }
}
