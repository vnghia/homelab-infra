import pulumi_docker as docker
from pulumi import ComponentResource, Output, ResourceOptions

from _common import vpn_config
from _container import DockerContainer
from _network.resource import child_opts


class VPN(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:device:VPN", "vpn", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.networks: dict = {}

        for name, config in vpn_config.items():
            vpn_type = config.pop("type")

            envs = {
                "VPN_SERVICE_PROVIDER": config.pop("provider"),
                "VPN_TYPE": vpn_type,
                "DNS_KEEP_NAMESERVER": "on",
            }
            for k, v in config.pop(vpn_type).items():
                envs["{}_{}".format(vpn_type, k).upper().replace("-", "_")] = v
            for k, v in config.items():
                envs[k.upper().replace("-", "_")] = v

            container = DockerContainer.build(
                "vpn-{}".format(name),
                opts=self.__child_opts,
                capabilities=docker.ContainerCapabilitiesArgs(adds=["NET_ADMIN"]),
                image="gluetun",
                envs=envs,
            )

            self.networks[name] = Output.concat("container:", container.id)

        self.register_outputs({})


vpn = VPN()
