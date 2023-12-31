from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "navidrome",
            "rule": Output.format("Host(`{0}`)", hostnames["public-navidrome"]),
            "sec_mode": "public",
        },
        "service": {"port": 4533},
    }
}
