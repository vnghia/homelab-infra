from pulumi import Output

from _common import get_logical_name
from _image import docker_image
from _network.docker import default_bridge_network

common_config = {
    "group": "Network",
    "requires_terminal": False,
}

script_config = {
    "Private port forwarding": {
        "script_type": "shell",
        "script_path": [
            "docker run --rm --network container:{} {} tcp-listen:$1,fork,reuseaddr tcp:$2:$3".format(
                get_logical_name("tailscale"),
                docker_image.image_map["socat"]["image_name"],
            ),
        ],
        "parameters": [
            {
                "name": "src_port",
                "required": True,
                "type": "int",
            },
            {
                "name": "dest_hostname",
                "required": True,
                "type": "list",
                "values": {
                    "script": Output.concat(
                        "docker ps --format '{{.Names}}' --filter network=",
                        default_bridge_network.name,
                    )
                },
            },
            {
                "name": "dest_port",
                "required": True,
                "type": "int",
            },
        ],
    },
}
