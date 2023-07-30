from _common import service_config

_wireguard_config = service_config["wireguard"]

output_config = {
    "path": "/config/wg0.conf",
    "input": _wireguard_config,
}
