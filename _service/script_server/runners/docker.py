from _service.script_server.docker import DOCKER_SCRIPT_SERVER_LABEL

common_config = {
    "group": "Docker",
    "requires_terminal": False,
    "script_type": "shell",
}

script_config = {
    "Stop and remove containers": {
        "script_path": [["docker", "rm", "-f", '"$@"']],
        "parameters": [
            {
                "name": "containers",
                "required": True,
                "type": "multiselect",
                "values": {
                    "script": "docker ps --format '{{.Names}}' --filter label="
                    + DOCKER_SCRIPT_SERVER_LABEL
                },
                "multiselect_argument_type": "argument_per_value",
            },
        ],
    },
}
