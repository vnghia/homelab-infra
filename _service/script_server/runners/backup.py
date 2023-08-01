from datetime import datetime

from _common import backup_config, container_storage_config

_script_server_volume = container_storage_config["script-server"]

common_config = {
    "group": "Backup & Restore",
    "working_directory": _script_server_volume["compose"]["dir"],
    "requires_terminal": False,
}

docker_compose_script = [
    "docker",
    "compose",
    "-f",
    "backup-compose.yaml",
    "run",
    "--rm",
]

service_list = list(backup_config.get("service", {}).keys())
service_input = {
    "name": "service",
    "param": "-s",
    "type": "multiselect",
    "values": service_list,
    "multiselect_argument_type": "argument_per_value",
}

script_config = {
    "Backup": {
        "script_path": docker_compose_script + ["backup", "backup"],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=0),
                "repeat_unit": "days",
                "repeat_period": 1,
            },
            "parameter_values": {"service": []},
        },
        "parameters": [service_input],
    },
    "Restore": {
        "script_path": docker_compose_script + ["backup", "restore"],
        "parameters": [
            service_input,
            {"name": "snapshot", "param": "--snapshot", "type": "text"},
        ],
    },
    "Prune backup": {
        "script_path": docker_compose_script + ["backup", "prune"],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=12),
                "repeat_unit": "weeks",
                "repeat_period": 2,
                "weekdays": ["sunday"],
            },
            "parameter_values": {"keep_last": 14},
        },
        "parameters": [
            {"name": "keep_last", "param": "-k", "type": "int", "min": 1},
        ],
    },
    "Check backup": {
        "script_path": docker_compose_script + ["backup", "check"],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=12),
                "repeat_unit": "weeks",
                "repeat_period": 1,
                "weekdays": ["saturday"],
            },
        },
        "parameters": [{"name": "read_data", "param": "-r", "no_value": True}],
    },
}
