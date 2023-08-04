from _common import constant, container_storage_config, get_logical_name

_script_server_volume = container_storage_config["script-server"]

docker_compose_dir = _script_server_volume["compose"]["dir"]


def build_compose_script(file: str, *args, name: str | None = None):
    return (
        [
            "docker",
            "compose",
            "-f",
            file,
            "run",
            "--rm",
        ]
        + (["--name", get_logical_name(name)] if name else [])
        + list(args)
    )


docker_label = []
for k, v in constant.PROJECT_TAG.items():
    docker_label += ["-l", "{}={}".format(k, v)]


def build_run_net_tailscale(name: str | None = None):
    return (
        [
            "docker",
            "run",
            "--rm",
            "--network",
            "container:{}".format(get_logical_name("tailscale")),
        ]
        + (["--name", get_logical_name(name)] if name else [])
        + docker_label
    )
