from _common import server_config
from _image import docker_image
from _service.script_server.docker import build_run_net_bridge

common_config = {
    "group": "Neko",
    "requires_terminal": False,
    "script_type": "shell",
}

neko_image_list = {
    v["image_name"]: k.removeprefix("neko-")
    for k, v in docker_image.image_map.items()
    if k.startswith("neko-")
}


def build_neko_param(name: str, no_value: bool = False, **kwargs):
    return (
        {
            "name": name,
            "same_arg_param": True,
        }
        | (
            {"param": "-e=NEKO_{}=".format(name.upper())}
            if not no_value
            else {"param": "-e=NEKO_{}=1".format(name.upper()), "no_value": True}
        )
        | kwargs
    )


script_config = {
    "Public neko": {
        "script_path": [
            build_run_net_bridge("$PARAM_NAME")
            + [
                "--shm-size",
                "$PARAM_SHM",
                "-p",
                "{0}:{0}/udp".format("$PARAM_EPR"),
                "-e=NEKO_BIND=:$PARAM_PORT",
                '"$@"',
                "$PARAM_IMAGE",
            ],
        ],
        "parameters": [
            {
                "name": "image",
                "required": True,
                "type": "list",
                "values": list(neko_image_list.keys()),
                "values_ui_mapping": neko_image_list,
                "pass_as": "env_variable",
            },
            {
                "name": "port",
                "required": True,
                "type": "int",
                "default": 9090,
                "pass_as": "env_variable",
            },
            build_neko_param("icelite", no_value=True, constant=True, default=True),
            build_neko_param(
                "nat1to1",
                constant=True,
                default="{}".format(
                    " ".join([server_config["ipv4"], server_config["ipv6"]])
                ),
            ),
            build_neko_param("hwenc", constant=True, default="none"),
            build_neko_param("password"),
            build_neko_param("password_admin"),
            build_neko_param("epr", default="52000-52100"),
            {
                "name": "shm",
                "required": True,
                "type": "text",
                "default": "2G",
                "pass_as": "env_variable",
            },
            {
                "name": "name",
                "required": True,
                "type": "text",
                "default": "public-neko",
                "pass_as": "env_variable",
            },
        ],
    },
}
