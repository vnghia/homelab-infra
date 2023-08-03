from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "paperless-ngx",
            "rule": Output.format(
                "Host(`{0}`)",
                hostnames["private-paperless-ngx"],
            ),
        },
        "service": {"port": 8000},
    }
}
