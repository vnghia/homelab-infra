from _common import service_config

_docker_browser_config = service_config["docker-browser"]

envs = {
    "DUFS_SERVE_PATH": _docker_browser_config["mount-root"],
    "DUFS_PORT": _docker_browser_config["port"],
    "DUFS_ALLOW_ALL": "true",
}
