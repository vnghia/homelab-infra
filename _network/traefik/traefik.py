from pathlib import Path

from pulumi import ComponentResource, Output, ResourceOptions

from _common import container_storage_config
from _container import DockerContainer
from _file import Template
from _network.dns.cloudflare import cloudflare_dns
from _network.resource import child_opts
from _network.tailscale import tailscale_device
from _network.traefik.config.dynamic_config import TraefikDynamicConfig

_traefik_volume = container_storage_config["traefik"]


class TraefikProxy(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:proxy:Traefik", "traefik", None, child_opts)

        self.__child_opts = ResourceOptions(parent=self)

        self.__build_static_config()
        self.__build_container()
        self.__build_dynamic_config()

        self.dynamic_config = self.__dynamic_config.dynamic_config

        self.register_outputs({"static_config": self.__static_config["content"]})

    def __build_static_config(self):
        self.__static_config = Template(self.__child_opts).build(
            module_path=Path(__file__).parent / "config" / "static.py"
        )

    def __build_container(self):
        # TODO: Re-enable healthcheck after https://github.com/traefik/traefik/issues/6861
        self.__container = DockerContainer.build(
            name="traefik",
            opts=self.__child_opts,
            command=[
                "--configFile={}{}".format(
                    _traefik_volume["config"]["dir"],
                    self.__static_config["config"]["path"],
                ),
            ],
            envs={
                "LEGO_DISABLE_CNAME_SUPPORT": "true",
                "CF_DNS_API_TOKEN": cloudflare_dns.acme_dns_token,
                "CF_ZONE_API_TOKEN": cloudflare_dns.acme_dns_token,
            },
            network_mode=Output.concat("container:", tailscale_device.container_id),
            volumes={
                "/etc/localtime": {"ro": True},
                "/usr/share/zoneinfo": {"ro": True},
            },
            labels={"static-config-sha256": self.__static_config["sha256"]},
        )

    def __build_dynamic_config(self):
        self.__dynamic_config = TraefikDynamicConfig(self.__child_opts)


traefik_proxy = TraefikProxy()
