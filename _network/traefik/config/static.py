from _common import container_storage_config, service_config

_tailscale_config = service_config["tailscale"]
_traefik_config = service_config["traefik"]
_traefik_volume = container_storage_config["traefik"]

_config_dir = _traefik_volume["config"]["dir"]
_config_volume = _traefik_volume["config"]["volume"]
_cert_dir = _traefik_volume["cert"]["dir"]
_acme_server = _traefik_config["acme"].get(
    "server", "https://acme-v02.api.letsencrypt.org/directory"
)
_acme_email = _traefik_config["acme"]["email"]

_tailscale_https_port = _tailscale_config["ports"]["https"]
_tailscale_http_port = _tailscale_config["ports"]["http"]


def build_config():
    input_dict = {
        "api": {"dashboard": True},
        "log": {"level": "INFO"},
        "ping": {},
        "accessLog": {"fields": {"names": {"StartUTC": "drop"}}},
        "entryPoints": {
            "https-private": {
                "address": "[::]:443",
                "forwardedHeaders": {"insecure": True},
            },
            "https-public": {
                "address": "[::]:{}".format(_tailscale_https_port),
            },
            "http-private": {
                "address": "[::]:80",
                "http": {
                    "redirections": {"entryPoint": {"to": ":443", "scheme": "https"}}
                },
            },
            "http-public": {
                "address": "[::]:{}".format(_tailscale_http_port),
                "http": {
                    "redirections": {"entryPoint": {"to": ":443", "scheme": "https"}}
                },
            },
        },
        "providers": {"file": {"directory": _config_dir, "watch": True}},
        "certificatesResolvers": {
            "leresolver_dns": {
                "acme": {
                    "caServer": _acme_server,
                    "email": _acme_email,
                    "storage": "{}{}".format(_cert_dir, "acme.json"),
                    "dnsChallenge": {"provider": "cloudflare"},
                }
            },
        },
    }

    experimental_dict = {}

    plugins_dict = {}
    for name, data in _traefik_config.get("plugin", {}).items():
        plugins_dict[name] = {"moduleName": data["name"], "version": data["version"]}
    if len(plugins_dict):
        experimental_dict["plugins"] = plugins_dict

    if len(experimental_dict):
        input_dict["experimental"] = experimental_dict

    return input_dict


output_config = {
    "name": "traefik-static",
    "volume": _config_volume,
    "path": "static.toml",
    "input": build_config(),
    "schema": _traefik_config["schema"]["static"],
}
