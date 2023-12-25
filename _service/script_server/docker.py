from _common import constant, container_storage_config, get_logical_name
from _network.docker import default_bridge_network

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


def __build_run_net(name: str | None = None, network: str | None = None):
    return (
        [
            "docker",
            "run",
            "--rm",
            "--network",
            network or default_bridge_network.name,
        ]
        + (["--name", get_logical_name(name)] if name else [])
        + docker_label
    )


def build_run_net_tailscale(name: str | None = None):
    return __build_run_net(
        name=name, network="container:{}".format(get_logical_name("tailscale"))
    )


def build_run_net_bridge(name: str | None = None):
    return __build_run_net(name)
