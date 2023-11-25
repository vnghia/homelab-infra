from _common import container_storage_config, get_logical_name

_crowdsec_volume = container_storage_config["crowdsec"]

output_config = {
    "name": "crowdsec-acquis-authelia",
    "volume": _crowdsec_volume["config"]["volume"],
    "path": "acquis.d/authelia.yaml",
    "input": {
        "source": "docker",
        "container_name": [get_logical_name("authelia")],
        "labels": {"type": "authelia"},
    },
}
