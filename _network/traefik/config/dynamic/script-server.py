from pulumi import Output

from _common import service_config
from _network.dns import hostnames

_script_server_config = service_config["script-server"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "script-server",
            "rule": Output.format("Host(`{0}`)", hostnames["private-script-server"]),
            "middlewares": ["script-server-user"],
        },
        "service": {"port": _script_server_config["port"]},
        "middleware": {
            "script-server-user": {
                "name": "headers",
                "customRequestHeaders": {
                    "X-Forwarded-User": _script_server_config["admin"]
                },
            }
        },
    }
}
