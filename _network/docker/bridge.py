import pulumi_docker as docker
from pulumi import ResourceOptions

from _common import constant, get_logical_name
from _network.resource import child_opts

default_bridge_network = docker.Network(
    get_logical_name("bridge"),
    opts=child_opts.merge(ResourceOptions(delete_before_replace=True)),
    name=get_logical_name("bridge"),
    driver="bridge",
    ipv6=True,
    labels=[
        docker.NetworkLabelArgs(label=k, value=v)
        for k, v in constant.PROJECT_TAG.items()
    ],
)
