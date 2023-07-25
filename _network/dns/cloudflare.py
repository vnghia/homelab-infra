import ipaddress

import pulumi_cloudflare as cloudflare
from pulumi import ComponentResource, Output, ResourceOptions

from _common import dns_config, get_logical_name, server_config
from _network.resource import child_opts
from _network.tailscale import tailscale_device


class CloudflareDNS(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:dns:Cloudflare", "cloudflare", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__build_zone_id()
        self.__build_records()
        self.__build_token()

        self.hostnames = {k: v.hostname for k, v in self.__records.items()}
        self.acme_dns_token = self.__token.value
        self.register_outputs(
            {"hostnames": self.hostnames, "acme_dns_token": self.acme_dns_token}
        )

    def __build_zone_id(self):
        self.__zone_id_map: dict[str, str] = {
            zone.name: zone.id
            for zone in [
                cloudflare.get_zone(account_id=dns_config["account-id"], name=name)
                for name in dns_config["zone"].keys()
            ]
        }

    def __build_records(self):
        self.__records: dict[str, cloudflare.Record] = {}
        self.__ip_map = {
            "public": {"address": server_config["ip"], "proxied": True},
            "private": {"address": tailscale_device.ipv4, "proxied": False},
        }

        for zone_name, zone_config in dns_config["zone"].items():
            zone_key = zone_config.pop("key", zone_name)
            zone_id = self.__zone_id_map[zone_name]
            self.__build_records_zone(zone_key, zone_id, zone_config)

    def __build_records_zone(self, key: str, id: str, config):
        for ip_type, ip_config in self.__ip_map.items():
            record_value = ip_config["address"]
            record_type = Output.from_input(record_value).apply(
                lambda address: "A"
                if ipaddress.ip_address(address).version == 4
                else "AAAA"
            )

            for record_key, record_name in config.get(ip_type, {}).items():
                full_key = "-".join(
                    ([key] if key != "main" else []) + [ip_type] + [record_key]
                )
                self.__records[full_key] = cloudflare.Record(
                    full_key,
                    opts=self.__child_opts,
                    name=record_name,
                    proxied=ip_config["proxied"],
                    type=record_type,
                    value=record_value,
                    zone_id=id,
                )

    def __build_token(self):
        permission_groups = cloudflare.get_api_token_permission_groups()

        self.__token_name = get_logical_name("acme-dns-token", add_project=True)
        self.__token = cloudflare.ApiToken(
            self.__token_name,
            opts=self.__child_opts.merge(ResourceOptions(delete_before_replace=True)),
            name=self.__token_name,
            policies=[
                cloudflare.ApiTokenPolicyArgs(
                    permission_groups=[
                        permission_groups.zone["Zone Read"],
                        permission_groups.zone["DNS Write"],
                    ],
                    resources={
                        "com.cloudflare.api.account.zone.{}".format(v): "*"
                        for v in self.__zone_id_map.values()
                    },
                )
            ],
        )


cloudflare_dns = CloudflareDNS()
