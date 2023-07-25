from pathlib import Path

import pulumi_docker as docker
import pulumi_random as random
import pulumi_tailscale as tailscale
from pulumi import ComponentResource, Output, ResourceOptions

from _command import Command
from _common import get_logical_name, tailscale_config
from _container import DockerContainer
from _data.docker import volume_map
from _network.resource import child_opts


class TailscaleDevice(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:device:Tailscale", "tailscale", None, child_opts)

        self.__child_opts = ResourceOptions(parent=self)
        self.__build_authkey()
        self.__build_hostname()
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
        # Manually replace authkey by calling
        # `pulumi up --replace 'urn:pulumi:dev::asky-observer::network:resource:root$network:device:Tailscale$tailscale:index/tailnetKey:TailnetKey::tailscale' -y`
        self.__authkey = tailscale.TailnetKey(
            "tailscale",
            opts=self.__child_opts,
            ephemeral=False,
            expiry=90 * 24 * 60 * 60,
            preauthorized=True,
            reusable=True,
        )

    def __build_hostname(self):
        self.__hostname_suffix = random.RandomString(
            "tailscale-suffix",
            opts=self.__child_opts,
            length=7,
            special=False,
            upper=False,
            keepers={"volume_name": volume_map[tailscale_config["state"]["volume"]]},
        )
        self.__hostname = Output.concat(
            get_logical_name(), "-", self.__hostname_suffix.result
        )

    def __build_cleanup(self):
        self.__cleanup = Command.build(
            "tailscale-cleanup-device",
            opts=self.__child_opts,
            update="",
            delete=Path(__file__).parent / "tailscale_cleanup_device.py",
            environment={"TAILSCALE_DEVICE_HOSTNAME": self.__hostname},
        )

    def __build_container(self):
        self.__container = DockerContainer.build(
            name="tailscale",
            opts=self.__child_opts,
            envs={
                "TS_AUTHKEY": self.__authkey.key,
                "TS_STATE_DIR": tailscale_config["state"]["dir"],
                "TS_SOCKET": tailscale_config["socket"],
            },
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=["CMD-SHELL", "tailscale status"],
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
                    internal=tailscale_config["port"]["internal"],
                    external=tailscale_config["port"]["external"],
                )
            ],
            volumes={
                tailscale_config["state"]["dir"]: {
                    "volume": tailscale_config["state"]["volume"]
                }
            },
            wait=True,
        )

    def __get_device(self):
        self.__device = tailscale.get_device_output(
            name=Output.all(
                hostname=self.__container.hostname,
                tailnet_name=tailscale_config["tailnet_name"],
                _=self.__container.id,
            ).apply(
                lambda args: "{}.{}".format(args["hostname"], args["tailnet_name"])
            ),
            wait_for="10s",
        )


tailscale_device = TailscaleDevice()