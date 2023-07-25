from pathlib import Path

import pulumi_docker as docker
from pulumi import ComponentResource, Output, ResourceOptions

from _common import traefik_config
from _container import DockerContainer
from _file import Template
from _network.dns import cloudflare_dns
from _network.resource import child_opts
from _network.tailscale import tailscale_device


class TraefikProxy(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:proxy:Traefik", "traefik", None, child_opts)

        self.__child_opts = ResourceOptions(parent=self)

        self.__build_static_config()
        self.__build_container()

        self.register_outputs({"static_config": self.__static_config["content"]})

    def __build_static_config(self):
        self.__static_config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "config" / "static.py"
        )

    def __build_container(self):
        self.__container = DockerContainer.build(
            name="traefik",
            opts=self.__child_opts.merge(ResourceOptions(delete_before_replace=True)),
            command=[
                "--configFile={}{}".format(
                    traefik_config["config"]["dir"],
                    self.__static_config["config"]["path"],
                ),
            ],
            envs={
                "LEGO_DISABLE_CNAME_SUPPORT": "true",
                "CF_DNS_API_TOKEN": cloudflare_dns.acme_dns_token,
                "CF_ZONE_API_TOKEN": cloudflare_dns.acme_dns_token,
            },
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=["CMD-SHELL", "traefik healthcheck --ping"],
                interval="1s",
                timeout="5s",
                retries=60,
            ),
            network_mode=Output.concat("container:", tailscale_device.container_id),
            volumes={
                traefik_config["config"]["dir"]: {
                    "name": traefik_config["config"]["volume"],
                    "ro": True,
                },
                traefik_config["cert"]["dir"]: {"name": traefik_config["cert"]["dir"]},
                "/etc/localtime": {"ro": True},
                "/usr/share/zoneinfo": {"ro": True},
            },
            wait=True,
            labels={"static-config-sha256": self.__static_config["sha256"]},
        )


traefik_proxy = TraefikProxy()
