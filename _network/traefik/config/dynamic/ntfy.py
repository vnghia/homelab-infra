from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "ntfy",
            "rule": Output.format("Host(`{0}`)", hostnames["public-ntfy"]),
            "sec_mode": "public",
        },
        "service": {"port": 80},
    }
}