import ipaddress

import pulumi_cloudflare as cloudflare
from pulumi import ComponentResource, Output, ResourceOptions

from _common import dns_config, get_logical_name, server_config
from _network.dns.hostnames import hostnames, records
from _network.resource import child_opts
from _network.tailscale import tailscale_device


class CloudflareDNS(ComponentResource):
    def __init__(self) -> None:
        super().__init__("network:dns:Cloudflare", "cloudflare", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__build_zone_id()
        self.__build_records()
        self.__build_token()

        self.acme_dns_token = self.__token.value
        self.register_outputs(
            {"hostnames": hostnames, "acme_dns_token": self.acme_dns_token}
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
        ip_map = {
            "public": {
                "addresses": {"v4": server_config["ipv4"], "v6": server_config["ipv6"]},
                "proxied": False,
            },
            "private": {
                "addresses": {"v4": tailscale_device.ipv4, "v6": tailscale_device.ipv6},
                "proxied": False,
            },
        }
        ip_child_opts = {
            k: ResourceOptions(
                parent=ComponentResource(
                    "network:dns:IP", k, None, opts=self.__child_opts
                )
            )
            for k in ip_map.keys()
        }

        for key, record in records.items():
            zone_id = self.__zone_id_map[record["zone"]]

            ip_config = ip_map[record["type"]]
            record_values = ip_config["addresses"]

            hostnames = []
            for record_value_key, record_value in record_values.items():
                record_type = Output.from_input(record_value).apply(
                    lambda address: "A"
                    if ipaddress.ip_address(address).version == 4
                    else "AAAA"
                )
                result = cloudflare.Record(
                    key + "-" + record_value_key,
                    opts=ip_child_opts[record["type"]],
                    name=record["name"],
                    proxied=ip_config["proxied"],
                    type=record_type,
                    value=record_value,
                    zone_id=zone_id,
                )
                hostnames.append(result.hostname)

            for hostname in hostnames:
                Output.all(local=record["hostname"], server=hostname).apply(
                    self.__compare_hostname
                )

    def __compare_hostname(self, args):
        if args["local"] != args["server"]:
            raise ValueError(
                "Local hostname ({}) is different from server hostname ({})."
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
