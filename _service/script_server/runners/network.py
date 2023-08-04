from pulumi import Output

from _common import get_logical_name
from _image import docker_image
from _network.docker import default_bridge_network
from _network.tailscale import tailscale_device

common_config = {
    "group": "Network",
    "requires_terminal": False,
    "script_type": "shell",
}

docker_run_net_tailscale = [
    "docker",
    "run",
    "--rm",
    "--network",
    "container:{}".format(get_logical_name("tailscale")),
]

browser_image_list = {
    v["image_name"]: k.removeprefix("neko-")
    for k, v in docker_image.image_map.items()
    if k.startswith("neko-")
}

script_config = {
    "Private port forwarding": {
        "script_path": [
            docker_run_net_tailscale
            + [
                docker_image.image_map["socat"]["image_name"],
                "tcp-listen:$1,fork,reuseaddr",
                "tcp:$2:$3",
            ]
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
    "Private browser": {
        "script_path": [
            docker_run_net_tailscale
            + [
                "--shm-size",
                "2G",
                "-e",
                "NEKO_SCREEN=1920x1080@60",
                "-e",
                "NEKO_BIND=:9090",
                "-e",
                "NEKO_ICELITE=1",
                "-e",
                "NEKO_IMPLICIT_CONTROL=1",
                "-e",
                "NEKO_HWENC=none",
                "-e",
                "NEKO_PATH_PREFIX=/digitalsea",
                "-e",
                tailscale_device.ipv4.apply(
                    lambda ipv4: "NEKO_NAT1TO1={}".format(ipv4)
                ),
                "$PARAM_BROWSER_IMAGE",
            ]
        ],
        "parameters": [
            {
                "name": "browser_image",
                "required": True,
                "type": "list",
                "values": list(browser_image_list.keys()),
                "values_ui_mapping": browser_image_list,
            },
        ],
    },
}
