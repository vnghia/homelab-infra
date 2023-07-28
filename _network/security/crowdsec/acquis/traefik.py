from _common import crowdsec_config, get_logical_name

output_config = {
    "name": "crowdsec-acquis-traefik",
    "volume": crowdsec_config["volume"]["config"]["volume"],
    "path": "acquis.d/traefik.yaml",
    "input": {
        "source": "docker",
        "container_name": [get_logical_name("traefik")],
        "labels": {"type": "traefik"},
    },
}
