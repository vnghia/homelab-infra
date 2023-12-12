from _common import container_storage_config, service_config

_dendrite_volume = container_storage_config["dendrite"]
_matrix_config = service_config["matrix"]

output_config = {
    "type": "raw",
    "name": "dendrite-key",
    "volume": _dendrite_volume["config"]["volume"],
    "path": "key.pem",
    "input": _matrix_config["dendrite"]["key"],
}
