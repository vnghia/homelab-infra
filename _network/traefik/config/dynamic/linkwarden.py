from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "linkwarden",
            "rule": Output.format("Host(`{0}`)", hostnames["private-linkwarden"]),
        },
        "service": {"port": 3000},
    }
}
