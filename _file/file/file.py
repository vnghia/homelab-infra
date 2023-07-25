import base64
import importlib
import json
from pathlib import Path
from typing import Callable

import httpx
import jsonschema
import tomlkit
from pulumi import Input, Output, ResourceOptions

from _command import Command
from _common import constant
from _container.image.image import docker_image
from _data.docker import volume_map


class File:
    @classmethod
    def build_container_file(
        cls,
        name: str,
        opts: ResourceOptions,
        volume: str,
        path: Input[str],
        content: Input[str],
    ):
        return cls.__build(
            "{}-file".format(name),
            opts=opts,
            path=path,
            content=content,
            create_path=Path(__file__).parent / "container" / "create.py",
            delete_path=Path(__file__).parent / "container" / "delete.py",
            environment={
                "DOCKER_ASSET_IMAGE": docker_image.image_map["workaround"]["image_id"],
                "DOCKER_ASSET_VOLUME": volume_map[volume],
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
            opts=opts.merge(ResourceOptions(delete_before_replace=True)),
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
    ):
        config = config or {}
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

        output_type_fn = {"toml": self.__build_toml_apply}
        output_type = config.get("type", config["path"].split(".")[-1])

        content = Output.json_dumps(config).apply(output_type_fn[output_type])
        output = File.build_container_file(
            config["name"],
            opts or self.__opts,
            config["volume"],
            config["path"],
            content,
        )

        return output | {"config": config, "content": content}

    def __build_toml_apply(self, config_str: str):
        config = json.loads(config_str)
        input = config["input"]
        if self.__middleware:
            input = self.__middleware(input, config)
        if "schema" in config:
            schema_req = httpx.get(config["schema"])
            schema_req.raise_for_status()
            jsonschema.validate(input, schema_req.json())
        return tomlkit.dumps(tomlkit.item(input), sort_keys=True)
