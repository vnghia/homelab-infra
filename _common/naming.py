from _common import constant


def get_logical_name(
    name: str | None = None, add_project: bool = False, add_stack: bool = True
):
    return "-".join(
        ([constant.PROJECT_NAME] if add_project or not name else [])
        + ([name] if name else [])
        + ([constant.PROJECT_STACK] if add_stack else [])
    )
