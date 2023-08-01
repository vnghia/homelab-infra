from _common import service_config

_script_server_config = service_config["script-server"]

output_config = {
    "path": "/app/conf/conf.json",
    "input": {
        "port": _script_server_config["port"],
        "access": {
            "admin_users": [_script_server_config["admin"]],
            "trusted_ips": [
                _script_server_config["admin"],
                "10.0.0.0/8",
                "172.16.0.0/12",
                "192.168.0.0/16",
            ],
        },
        "logging": {
            "execution_file": "${SCRIPT}-${DATE}.log",
            "execution_date_format": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
}
