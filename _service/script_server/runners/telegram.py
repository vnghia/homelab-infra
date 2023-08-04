from datetime import datetime

from _common import get_logical_name
from _service.script_server.docker import build_compose_script, docker_compose_dir

common_config = {
    "group": "Telegram",
    "working_directory": docker_compose_dir,
    "requires_terminal": False,
    "script_type": "shell",
}

docker_compose_script = build_compose_script("telegram-compose.yaml")
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
