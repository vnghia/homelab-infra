from _common import service_config
from _network.docker import default_bridge_network

_script_server_config = service_config["script-server"]

output_config = {
    "path": "/app/conf/conf.json",
    "input": {
        "port": _script_server_config["port"],
        "access": {
            "admin_users": [_script_server_config["admin"]],
            "trusted_ips": default_bridge_network.ipam_configs.apply(
                lambda configs: [config.subnet for config in configs]
            ),
            "user_header_name": "X-Forwarded-User",
        },
        "logging": {
            "execution_file": "${SCRIPT}-${DATE}.log",
            "execution_date_format": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
}
