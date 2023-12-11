from _secret import secret

output_config = {
    "input": {
        "type": "http",
        "middleware": {
            "crowdsec": {
                "name": "crowdsec",
                "plugin": True,
                "enabled": True,
                "crowdsecMode": "stream",
                "crowdseclapikey": secret.keys["crowdsec-traefik-bouncer"].result,
            }
        },
    }
}
