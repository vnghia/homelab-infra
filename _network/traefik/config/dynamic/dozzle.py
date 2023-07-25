from pulumi import Output

from _network.dns.cloudflare import cloudflare_dns

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "dozzle",
            "rule": Output.format(
                "Host(`{0}`) && PathPrefix(`/log`)",
                cloudflare_dns.hostnames["private-infra"],
            ),
        },
        "service": {"port": 8080},
    }
}
