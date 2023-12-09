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
            }
        },
    }
}
