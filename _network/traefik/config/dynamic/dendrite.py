from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "dendrite",
            "rule": Output.format("Host(`{0}`)", hostnames["public-dendrite"]),
            "sec_mode": "public",
        },
        "service": {"port": 8008},
    }
}
