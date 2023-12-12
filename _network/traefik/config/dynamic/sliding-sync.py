from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "sliding-sync",
            "rule": Output.format("Host(`{0}`)", hostnames["public-sliding-sync"]),
            "sec_mode": "public",
        },
        "service": {"port": 8008},
    }
}
