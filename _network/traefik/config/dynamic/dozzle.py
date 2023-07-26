from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "dozzle",
            "rule": Output.format(
                "Host(`{0}`) && PathPrefix(`/log`)",
                hostnames["private-infra"],
            ),
        },
        "service": {"port": 8080},
    }
}
