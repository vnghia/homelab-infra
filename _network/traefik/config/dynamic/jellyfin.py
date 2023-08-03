from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "jellyfin",
            "rule": Output.format("Host(`{0}`)", hostnames["private-jellyfin"]),
        },
        "service": {"port": 8096},
    }
}
