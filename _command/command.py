import sys
from pathlib import Path

import pulumi_command as command
from pulumi import ResourceOptions

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
        environment = kwargs.get("environment", {})
        return command.local.Command(
            name,
            opts=opts.merge(
                ResourceOptions(delete_before_replace=delete_before_replace)
            ),
            create=cls.__build_command(create),
            delete=cls.__build_command(delete),
            update=cls.__build_command(update),
            interpreter=kwargs.pop("interpreter", [cls.PYTHON_EXECUTABLE, "-c"]),
            triggers=list(environment.keys())
            + list(environment.values())
            + kwargs.pop("triggers", []),
            **kwargs,
        )
