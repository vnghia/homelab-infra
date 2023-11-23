from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "authelia",
            "rule": Output.format("Host(`{0}`)", hostnames["public-authelia"]),
            "sec_mode": "public",
        },
        "service": {"port": 9091},
    }
}
