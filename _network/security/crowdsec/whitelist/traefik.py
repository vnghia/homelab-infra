from _common import container_storage_config, service_config

_crowdsec_volume = container_storage_config["crowdsec"]
_traefik_config = service_config["traefik"]

output_config = {
    "name": "crowdsec-whitelist-traefik",
    "volume": _crowdsec_volume["config"]["volume"],
    "path": "parsers/s02-enrich/traefik.yaml",
    "input": {
        "name": "crowdsecurity/whitelists",
        "description": "whitelist traefik based on router name",
        "whitelist": {
            "reason": "traefik false positive",
            "expression": [
                'evt.Parsed.traefik_router_name == "{}"'.format(router)
                for router in _traefik_config.get("whitelist", {}).get("router", [])
            ],
        },
    },
}
