import base64
import configparser
import importlib
import io
import json
from pathlib import Path
from typing import Callable

import httpx
import jsonschema
import tomlkit
import yaml
from pulumi import Input, Output, ResourceOptions

from _command import Command
from _common import constant
from _image import docker_image


class File:
    @classmethod
    def build_container_file(
        cls,
        name: str,
        opts: ResourceOptions,
        path: Input[str],
        content: Input[str],
        volume: str | None = None,
        docker_asset_volume: Input[str] | None = None,
    ):
        if not docker_asset_volume:
            from _data.docker import volume_map

            docker_asset_volume = volume_map[volume]
        return cls.__build(
            "{}-file".format(name),
            opts=opts,
            path=path,
            content=content,
            create_path=Path(__file__).parent / "container" / "create.py",
            delete_path=Path(__file__).parent / "container" / "delete.py",
            environment={
                "DOCKER_ASSET_IMAGE": docker_image.image_map["workaround"]["image_id"],
                "DOCKER_ASSET_VOLUME": docker_asset_volume,
            },
        )

    @classmethod
    def __build(
        cls,
        name: str,
        opts: ResourceOptions,
        path: Input[str],
        content: Input[str],
        create_path: Path,
        delete_path: Path,
        **kwargs
    ):
        # TODO: Checking for diff (the content of this file and does it still exist)
        # Blocked by: https://github.com/pulumi/pulumi-command/issues/20
        file = Command.build(
            name,
            opts=opts,
            create=create_path,
            delete=delete_path,
            stdin=Output.from_input(content).apply(
                lambda content: base64.standard_b64encode(content.encode()).decode(),
            ),
            environment={"FILE_PATH": path} | kwargs.pop("environment", {}),
            **kwargs
        )
        return {"file": file, "sha256": file.stdout}


class Template:
    def __init__(
        self,
        opts: ResourceOptions | None = None,
        middleware: Callable[[dict, dict], dict] | None = None,
    ) -> None:
        self.__opts = opts
        self.__middleware = middleware

    def build(
        self,
        opts: ResourceOptions | None = None,
        module_path: str | Path | None = None,
        config: dict | None = None,
        input_args: dict | None = None,
        docker_asset_volume: Input[str] | None = None,
        input_fn: Callable[[dict], dict] | None = None,
    ):
        config = config or {}
        opts = opts or self.__opts
        if module_path:
            module = importlib.import_module(
                str(
                    Path(module_path)
                    .resolve()
                    .relative_to(constant.PROJECT_ROOT_DIR)
                    .with_suffix("")
                ).replace("/", ".")
            )
            config = config | module.output_config
        if input_fn:
            config = input_fn(config)
        if "input_fn" in config:
            config["input"] = config.pop("input_fn")(opts, input_args)

        output_type_fn = {
            "toml": self.__build_toml_apply,
            "conf": self.__build_conf_apply,
            "yaml": self.__build_yaml_apply,
        }
        output_type = config.get("type", config["path"].split(".")[-1])

        content = Output.json_dumps(config).apply(output_type_fn[output_type])
        output = File.build_container_file(
            config["name"],
            opts=opts,
            path=config["path"],
            content=content,
            volume=config.get("volume"),
            docker_asset_volume=docker_asset_volume,
        )

        return output | {"config": config, "content": content}

    def __build_apply(self, config_str: str):
        config = json.loads(config_str)
        input = config["input"]
        if self.__middleware:
            input = self.__middleware(input, config)
        if "schema" in config:
            schema_req = httpx.get(config["schema"])
            schema_req.raise_for_status()
            jsonschema.validate(input, schema_req.json())
        return input, config

    def __build_toml_apply(self, config_str: str):
        input, _ = self.__build_apply(config_str)
        return tomlkit.dumps(tomlkit.item(input), sort_keys=True)

    def __build_conf_apply(self, config_str: str):
        input, _ = self.__build_apply(config_str)

        parser = configparser.ConfigParser()
        for remote_name, remote in input.items():
            parser.add_section(remote_name)
            for k, v in remote.items():
                parser.set(remote_name, k, v)
        config_content = io.StringIO()
        parser.write(config_content)
        config_content.seek(0)

        return config_content.read()

    def __build_yaml_apply(self, config_str: str):
        input, _ = self.__build_apply(config_str)
        return yaml.dump(input, default_flow_style=False)
