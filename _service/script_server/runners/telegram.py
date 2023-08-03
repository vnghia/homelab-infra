from datetime import datetime

from _common import container_storage_config, get_logical_name

_script_server_volume = container_storage_config["script-server"]

common_config = {
    "group": "Telegram",
    "working_directory": _script_server_volume["compose"]["dir"],
    "requires_terminal": False,
    "script_type": "shell",
}

docker_compose_script = [
    "docker",
    "compose",
    "-f",
    "telegram-compose.yaml",
    "run",
    "--rm",
]
docker_restart = ["docker", "restart", get_logical_name("telegram-login-code")]

script_config = {
    "Login telegram": {
        "script_path": [docker_compose_script + ["login"]] + [docker_restart],
        "requires_terminal": True,
    },
    "Refresh telegram session": {
        "script_path": [docker_compose_script + ["refresh_session"]] + [docker_restart],
        "scheduling": {
            "schedule": {
                "start_datetime": datetime.fromtimestamp(0).replace(hour=0),
                "repeat_unit": "weeks",
                "repeat_period": 1,
                "weekdays": ["sunday"],
            },
        },
    },
}
