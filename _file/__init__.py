import pulumi

try:
    from _file.file.file import CONF_NO_SECTION_HEADER, File, Template

    __all__ = ["CONF_NO_SECTION_HEADER", "File", "Template"]
except KeyError:
    if pulumi.get_project() != "project":  # running with pulumi runtime
        raise
