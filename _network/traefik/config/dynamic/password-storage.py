from pulumi import Output

from _common import service_config
from _network.dns import hostnames

_password_storage_config = service_config["password-storage"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "password-storage",
            "rule": Output.format("Host(`{0}`)", hostnames["public-password-storage"]),
            "sec_mode": "public",
            "middlewares": ["authelia-forward-auth"],
        },
        "service": {"port": _password_storage_config["port"]},
    }
}
