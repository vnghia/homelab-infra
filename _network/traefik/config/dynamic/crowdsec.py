import pulumi_cloudflare as cloudflare
from pulumi import ResourceOptions

from _network.security import crowdsec


def input_fn(opts: ResourceOptions, _):
    input_dict = {
        "type": "http",
        "middleware": {
            "crowdsec": {
                "name": "crowdsec",
                "plugin": True,
                "enabled": True,
                "crowdsecMode": "stream",
                "crowdseclapikey": crowdsec.add_bouncer("traefik", opts=opts),
                "forwardedheaderstrustedips": cloudflare.get_ip_ranges().cidr_blocks,
            }
        },
    }
    return input_dict


output_config = {"input_fn": input_fn}
