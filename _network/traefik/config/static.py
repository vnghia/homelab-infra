import pulumi_cloudflare as cloudflare

from _common import tailscale_config, traefik_config

__config_dir = traefik_config["config"]["dir"]
__config_volume = traefik_config["config"]["volume"]
__cert_dir = traefik_config["cert"]["dir"]
__acme_server = traefik_config["acme"].get(
    "server", "https://acme-v02.api.letsencrypt.org/directory"
)
__acme_email = traefik_config["acme"]["email"]


def build_config():
    input_dict = {
        "api": {"dashboard": True},
        "log": {"level": "INFO"},
        "ping": {},
        "accessLog": {"fields": {"names": {"StartUTC": "drop"}}},
        "entryPoints": {
            "https-private": {"address": ":443"},
            "https-public": {
                "address": ":{}".format(tailscale_config["port"]["internal"]),
                "forwardedHeaders": {
                    "trustedIPs": cloudflare.get_ip_ranges().cidr_blocks
                },
            },
        },
        "providers": {"file": {"directory": __config_dir, "watch": True}},
        "certificatesResolvers": {
            "leresolver_dns": {
                "acme": {
                    "caServer": __acme_server,
                    "email": __acme_email,
                    "storage": "{}{}".format(__cert_dir, "acme-dns.json"),
                    "dnsChallenge": {"provider": "cloudflare"},
                }
            },
        },
    }

    experimental_dict = {}

    plugins_dict = {}
    for name, data in traefik_config.get("plugin", {}).items():
        plugins_dict[name] = {"moduleName": data["name"], "version": data["version"]}
    if len(plugins_dict):
        experimental_dict["plugins"] = plugins_dict

    if len(experimental_dict):
        input_dict["experimental"] = experimental_dict

    return input_dict


output_config = {
    "name": "traefik-static",
    "volume": __config_volume,
    "path": "static.toml",
    "input": build_config(),
    "schema": traefik_config["schema"]["static"],
}
