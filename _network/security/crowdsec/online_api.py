from _common import container_storage_config, service_config

_crowdsec_config = service_config["crowdsec"]
_crowdsec_volume = container_storage_config["crowdsec"]

output_config = {
    "name": "crowdsec-online-api",
    "volume": _crowdsec_volume["config"]["volume"],
    "path": "online_api_credentials.yaml",
    "input": {
        "url": "https://api.crowdsec.net/",
        "login": _crowdsec_config["online"]["login"],
        "password": _crowdsec_config["online"]["password"],
    },
}
