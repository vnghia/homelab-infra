from pulumi import Output

from _image import docker_image
from _network.docker import default_bridge_network
from _network.tailscale import tailscale_device
from _service.script_server.docker import build_run_net_tailscale

common_config = {
    "group": "Network",
    "requires_terminal": False,
    "script_type": "shell",
}

script_config = {
    "Private port forwarding": {
        "script_path": [
            ["PARAM_SCR_PORT=$1"],
            ["PARAM_DEST_HOSTNAME=$2"],
            ["PARAM_DEST_PORT=$3"],
            [
                "echo",
                tailscale_device.ipv4.apply(
                    lambda ipv4: "http://{}:${{PARAM_SCR_PORT}}".format(ipv4)
                ),
            ],
            build_run_net_tailscale()
            + [
                "--name",
                "port-forwarding-${PARAM_SCR_PORT}-${PARAM_DEST_HOSTNAME}-${PARAM_DEST_PORT}",
            ]
            + [
                docker_image.image_map["socat"]["image_name"],
                "tcp-listen:${PARAM_SCR_PORT},fork,reuseaddr",
                "tcp:${PARAM_DEST_HOSTNAME}:${PARAM_DEST_PORT}",
            ],
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
