import deepmerge
import pulumi


def __build_config(key: str) -> dict:
    return deepmerge.always_merger.merge(
        pulumi.Config().get_object(key, {}),
        pulumi.Config().get_object("stack-{}".format(key), {}),
    )


docker_config = __build_config("docker")
server_config = __build_config("server")
dns_config = __build_config("dns")
storage_config = __build_config("storage")
secret_config = __build_config("secret_")
service_config = __build_config("service")

volume_config = storage_config.get("volume", {})


def __build_container_storage():
    __config = storage_config.get("container", {})
    for ks, vs in __config.items():
        for kc, vc in vs.items():
            if "volume" not in vc:
                volume = "{}-{}".format(ks, kc)
                assert volume in volume_config.get("local", {})
                vc["volume"] = volume
    return __config


storage_config["aws"] = {
    "AWS_ACCESS_KEY_ID": storage_config["key-id"],
    "AWS_SECRET_ACCESS_KEY": storage_config["key-secret"],
}

container_storage_config = __build_container_storage()
