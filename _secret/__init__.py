import pulumi

try:
    from _secret.secret import secret

    __all__ = ["secret"]
except KeyError:
    if pulumi.get_project() != "project":  # running with pulumi runtime
        raise
