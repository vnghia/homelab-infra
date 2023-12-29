from pathlib import Path

import pulumi_docker as docker
import pulumi_tailscale as tailscale
from pulumi import ComponentResource, Output, ResourceOptions

from _command import Command
from _common import container_storage_config, get_logical_name, service_config
from _container import DockerContainer
from _data.docker import volume_map
from _network.resource import child_opts

_tailscale_config = service_config["tailscale"]
_tailscale_volume = container_storage_config["tailscale"]


class TailscaleDevice(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:device:Tailscale", "tailscale", None, child_opts)

        self.__child_opts = ResourceOptions(parent=self)

        self.__hostname = get_logical_name()
        self.__state_volume_name = volume_map[_tailscale_volume["state"]["volume"]]
        self.__build_authkey()
        self.__build_cleanup()
        self.__build_container()

        self.__get_device()
        self.container_id = self.__container.id
        self.ipv4 = self.__device.addresses[0]
        self.ipv6 = self.__device.addresses[1]
        self.register_outputs(
            {"container_id": self.container_id, "ipv4": self.ipv4, "ipv6": self.ipv6}
        )

    def __build_authkey(self):
        self.__authkey = tailscale.TailnetKey(
            "tailscale",
            opts=self.__child_opts,
            description=self.__state_volume_name,
            ephemeral=False,
            expiry=5 * 60,
            preauthorized=True,
            reusable=False,
        )

    def __build_cleanup(self):
        self.__cleanup = Command.build(
            "tailscale-cleanup-device",
            opts=self.__child_opts,
            update="",
            delete=Path(__file__).parent / "tailscale_cleanup_device.py",
            environment={"TAILSCALE_DEVICE_HOSTNAME": self.__hostname},
            triggers=[self.__state_volume_name],
        )

    def __build_container(self):
        self.__container = DockerContainer.build(
            name="tailscale",
            opts=self.__child_opts,
            capabilities=docker.ContainerCapabilitiesArgs(adds=["NET_ADMIN"]),
            envs={
                "TS_AUTHKEY": self.__authkey.key,
                "TS_STATE_DIR": _tailscale_volume["state"]["dir"],
                "TS_SOCKET": _tailscale_config["socket"],
                "TS_USERSPACE": "false",
                "TS_AUTH_ONCE": "true",
            },
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=["CMD", "tailscale", "status"],
                interval="1s",
                timeout="5s",
                retries=60,
            ),
            hostname=self.__hostname,
            hosts=[
                docker.ContainerHostArgs(host="host.docker.internal", ip="host-gateway")
            ],
            ports=[
                docker.ContainerPortArgs(
                    internal=_tailscale_config["ports"]["http"],
                    external=80,
                ),
                docker.ContainerPortArgs(
                    internal=_tailscale_config["ports"]["http"],
                    external=80,
                    ip="::",
                ),
                docker.ContainerPortArgs(
                    internal=_tailscale_config["ports"]["https"],
                    external=443,
                ),
                docker.ContainerPortArgs(
                    internal=_tailscale_config["ports"]["https"],
                    external=443,
                    ip="::",
                ),
            ],
            sysctls={
                "net.ipv6.conf.all.disable_ipv6": 0,
                "net.ipv6.conf.all.forwarding": 1,
                "net.ipv6.conf.all.proxy_ndp": 1,
            },
            wait=True,
        )

    def __get_device(self):
        self.__device = tailscale.get_device_output(
            name=Output.all(
                hostname=self.__container.hostname,
                tailnet_name=_tailscale_config["tailnet_name"],
                _=self.__container.id,
            ).apply(
                lambda args: "{}.{}".format(args["hostname"], args["tailnet_name"])
            ),
            wait_for="10s",
        )


tailscale_device = TailscaleDevice()
