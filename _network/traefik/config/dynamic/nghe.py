from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "nghe",
            "rule": Output.format("Host(`{0}`)", hostnames["public-nghe"]),
            "sec_mode": "public",
        },
        "service": {"port": 3000},
    }
}
