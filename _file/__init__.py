import pulumi

try:
    from _file.file.file import File, Template

    __all__ = ["File", "Template"]
except KeyError:
    if pulumi.get_project() != "project":  # running with pulumi runtime
        raise
