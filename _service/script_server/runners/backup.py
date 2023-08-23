from datetime import datetime

from _common import backup_config
from _service.script_server.docker import build_compose_script, docker_compose_dir

common_config = {
    "group": "Backup & Restore",
    "working_directory": docker_compose_dir,
    "requires_terminal": False,
}

service_list = list(backup_config.get("service", {}).keys())
service_input = {
    "name": "service",
    "param": "-s",
    "type": "multiselect",
    "values": service_list,
    "multiselect_argument_type": "argument_per_value",
}

docker_compose_script = build_compose_script("backup-compose.yaml", "backup")

script_config = {
    "Backup": {
        "script_path": docker_compose_script + ["backup"],
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
        "script_path": docker_compose_script + ["restore"],
        "parameters": [
            service_input,
            {"name": "snapshot", "param": "--snapshot", "type": "text"},
        ],
    },
    "Prune backup": {
        "script_path": docker_compose_script + ["prune"],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=12),
                "repeat_unit": "weeks",
                "repeat_period": 2,
                "weekdays": ["saturday"],
            },
            "parameter_values": {"keep_last": "14"},
        },
        "parameters": [
            {"name": "keep_last", "param": "-k", "type": "int", "min": 1},
        ],
    },
    "Check backup": {
        "script_path": docker_compose_script + ["check"],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=12),
                "repeat_unit": "weeks",
                "repeat_period": 1,
                "weekdays": ["sunday"],
            },
        },
        "parameters": [{"name": "read_data", "param": "-r", "no_value": True}],
    },
}
