import pulumi_cloudflare as cloudflare

from _network.security import crowdsec

output_config = {
    "input": {
        "type": "http",
        "middleware": {
            "crowdsec": {
                "name": "crowdsec",
                "plugin": True,
                "enabled": True,
                "crowdsecMode": "stream",
                "crowdseclapikey": crowdsec.bouncer_key,
                "forwardedheaderstrustedips": cloudflare.get_ip_ranges().cidr_blocks,
            }
        },
    }
}
