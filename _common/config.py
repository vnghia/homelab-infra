import deepmerge
import pulumi


def __build_config(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker_config = __build_config("docker")
server_config = __build_config("server")
tailscale_config = __build_config("tailscale")
dns_config = __build_config("dns")
