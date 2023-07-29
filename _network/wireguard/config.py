from _common import container_storage_config, service_config

_wireguard_config = service_config["wireguard"]
_wireguard_volume = container_storage_config["wireguard"]

output_config = {
    "type": "conf",
    "name": "wireguard-config",
    "volume": _wireguard_volume["config"]["volume"],
    "path": "wg0.conf",
    "input": _wireguard_config,
}
