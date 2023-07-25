from pulumi import Output

from _network.dns.cloudflare import cloudflare_dns

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "traefik",
            "rule": Output.format(
                "Host(`{0}`) && (PathPrefix(`/proxy`) || HeaderRegexp(`Referer`, `.*/proxy/.*`))",
                cloudflare_dns.hostnames["private-infra"],
            ),
            "service": "api@internal",
            "middlewares": ["traefik-api-strip-prefix"],
        },
        "middleware": {
            "traefik-api-strip-prefix": {"name": "stripPrefix", "prefixes": ["/proxy"]}
        },
    }
}
