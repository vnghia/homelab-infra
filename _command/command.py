import sys
from pathlib import Path

import pulumi_command as command
from pulumi import Output, ResourceOptions

from _common import constant


class Command:
    PYTHON_EXECUTABLE = str(
        Path(sys.executable).relative_to(constant.PROJECT_ROOT_DIR).parent / "python3"
    )

    @classmethod
    def __build_command(cls, command_src: Path | str | None):
        if isinstance(command_src, Path):
            return open(command_src, "r").read()
        else:
            return command_src

    @classmethod
    def build(
        cls,
        name: str,
        opts: ResourceOptions,
        create: Path | str | None = None,
        delete: Path | str | None = None,
        update: Path | str | None = None,
        delete_before_replace: bool = True,
        **kwargs
    ):
        source_environment = kwargs.pop("environment", {})
        environment = {k.removeprefix("__"): v for k, v in source_environment.items()}
        trigger_environment = [
            Output.format("{}={}", k, v)
            for k, v in source_environment.items()
            if not (
                k.startswith("__")
                or k.endswith("CONTAINER_ID")
                or k.endswith("IMAGE_ID")
            )
        ]

        return command.local.Command(
            name,
            opts=opts.merge(
                ResourceOptions(delete_before_replace=delete_before_replace)
            ),
            create=cls.__build_command(create),
            delete=cls.__build_command(delete),
            update=cls.__build_command(update),
            interpreter=kwargs.pop("interpreter", [cls.PYTHON_EXECUTABLE, "-c"]),
            environment=environment,
            triggers=trigger_environment + kwargs.pop("triggers", []),
            **kwargs,
        )
