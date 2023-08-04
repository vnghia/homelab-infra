from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "neko-browser",
            "rule": Output.format(
                "Host(`{0}`) && PathPrefix(`/digitalsea`)",
                hostnames["private-infra"],
            ),
        },
        "service": {"host": "localhost", "port": 9090},
    }
}
