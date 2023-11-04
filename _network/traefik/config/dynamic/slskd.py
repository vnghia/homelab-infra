from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "slskd",
            "rule": Output.format(
                "Host(`{0}`)",
                hostnames["private-slskd"],
            ),
        },
        "service": {"port": 5030},
    }
}
