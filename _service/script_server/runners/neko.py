from pulumi import Output

from _common import server_config
from _image import docker_image
from _network.dns.hostnames import hostnames
from _network.tailscale import tailscale_device
from _secret import secret
from _service.script_server.docker import (
    build_run_net_bridge,
    build_run_net_tailscale,
    build_traefik_label,
)

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


def build_script_config():
    modes = ["public", "private"]

    script_paths = {
        k: (
            build_run_net_bridge("$PARAM_NAME")
            + ["-p", "{0}:{0}/udp".format("$PARAM_EPR")]
            if k == "public"
            else build_run_net_tailscale("$PARAM_NAME")
        )
        + build_traefik_label(
            name="$PARAM_NAME",
            rule="Host(\\`$PARAM_HOST\\`) && PathPrefix(\\`${PARAM_PATH_PREFIX%?}\\`)",
            port="$PARAM_PORT",
            sec_mode=k,
        )
        + [
            "--no-healthcheck",
            "--shm-size",
            "$PARAM_SHM",
            "-e=NEKO_BIND=:$PARAM_PORT",
            '"$@"',
            "$PARAM_IMAGE",
        ]
        for k in modes
    }

    names = {
        k: {
            "name": "name",
            "required": True,
            "type": "text",
            "default": "{}-neko".format(k),
            "pass_as": "env_variable",
        }
        for k in modes
    }

    prefixes = {"public": "/", "private": "/digitalsea/"}

    nat1to1s = {
        k: (
            "{}".format(" ".join([server_config["ipv4"], server_config["ipv6"]]))
            if k == "public"
            else Output.format("{0} {1}", tailscale_device.ipv4, tailscale_device.ipv6)
        )
        for k in modes
    }

    random_password = {
        "script": "cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1",
        "shell": True,
    }
    password_admins = {
        "public": random_password,
        "private": secret.accounts["private-neko"]["password"],
    }

    return {
        "{} neko".format(k.capitalize()): {
            "script_path": [
                ["echo", "$PARAM_PASSWORD_ADMIN"],
                ["echo", "$PARAM_PASSWORD"],
                script_paths[k],
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
                    "name": "host",
                    "required": True,
                    "type": "text",
                    "pass_as": "env_variable",
                }
                | ({} if k == "public" else {"default": hostnames["private-infra"]}),
                {
                    "name": "port",
                    "required": True,
                    "type": "int",
                    "default": 9090,
                    "pass_as": "env_variable",
                },
                build_neko_param("icelite", no_value=True, constant=True, default=True),
                build_neko_param("proxy", no_value=True, constant=True, default=True),
                build_neko_param(
                    "nat1to1",
                    constant=True,
                    default=nat1to1s[k],
                ),
                build_neko_param("hwenc", constant=True, default="none"),
                build_neko_param("screen", constant=True, default="1920x1080@30"),
                build_neko_param("path_prefix", default=prefixes[k]),
                build_neko_param("password", secure=True, default=random_password),
                build_neko_param(
                    "password_admin", secure=True, default=password_admins[k]
                ),
                build_neko_param("epr", default="52000-52100"),
                {
                    "name": "shm",
                    "required": True,
                    "type": "text",
                    "default": "2G",
                    "pass_as": "env_variable",
                },
                names[k],
            ],
        }
        for k in modes
    }


script_config = build_script_config()
