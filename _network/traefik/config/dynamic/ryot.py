from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "ryot",
            "rule": Output.format(
                "Host(`{0}`)",
                hostnames["private-ryot"],
            ),
        },
        "service": {"port": 8000},
    }
}
