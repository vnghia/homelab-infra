from _common import get_logical_name

output_config = {
    "path": "/etc/crowdsec/acquis.d/traefik.yaml",
    "input": {
        "source": "docker",
        "container_name": [get_logical_name("traefik")],
        "labels": {"type": "traefik"},
    },
}
