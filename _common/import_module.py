import importlib
from pathlib import Path

from _common import constant


def import_module(module_path: str | Path):
    return importlib.import_module(
        str(
            Path(module_path)
            .resolve()
            .relative_to(constant.PROJECT_ROOT_DIR)
            .with_suffix("")
        ).replace("/", ".")
    )
