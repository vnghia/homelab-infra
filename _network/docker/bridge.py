import pulumi_docker as docker

from _common import constant, get_logical_name

default_bridge_network = docker.Network(
    get_logical_name("bridge"),
    driver="bridge",
    labels=[
        docker.NetworkLabelArgs(label=k, value=v)
        for k, v in constant.PROJECT_TAG.items()
    ],
)
