from _common import crowdsec_config

output_config = {
    "name": "crowdsec-online-api",
    "volume": crowdsec_config["volume"]["config"]["volume"],
    "path": "online_api_credentials.yaml",
    "input": {
        "url": "https://api.crowdsec.net/",
        "login": crowdsec_config["online"]["login"],
        "password": crowdsec_config["online"]["password"],
    },
}
