from pulumi import ResourceOptions

from _command import Command
from _common import aws, get_logical_name, storage_config, volume_config
from _secret import secret


def input_fn(opts: ResourceOptions, _):
    bucket_name = storage_config["bucket"]
    input_dict = {
        "bucket": {
            "type": "s3",
            "provider": "Other",
            "region": storage_config["region"],
            "access_key_id": storage_config["key-id"],
            "secret_access_key": storage_config["key-secret"],
            "endpoint": storage_config["endpoint"],
        }
    }
    for name, prefix in volume_config.get("crypt", {}).items():
        password = secret.build_password("crypt-{}".format(name), opts=opts, length=32)
        password_obscured = Command.build(
            "rclone:obscure:{}".format(name),
            opts=opts,
            create="rclone obscure -",
            stdin=password.result,
            interpreter=["/bin/sh", "-c"],
        )
        salt = secret.build_password("crypt-{}-salt".format(name), opts=opts, length=32)
        salt_obscured = Command.build(
            "rclone:obscure:{}-salt".format(name),
            opts=opts,
            create="rclone obscure -",
            stdin=salt.result,
            interpreter=["/bin/sh", "-c"],
        )

        aws.build_cleanup(
            "crypt-{}-cleanup".format(name),
            opts=opts,
            prefix=prefix,
            triggers=[password, salt],
        )

        input_dict["crypt-{}-{}".format(bucket_name, name)] = {
            "type": "crypt",
            "remote": "bucket:{}/{}".format(bucket_name, prefix),
            "password": password_obscured.stdout,
            "password2": salt_obscured.stdout,
        }
    combine = []
    for name, path in volume_config.get("combine", {}).items():
        type, key = name.split("-", maxsplit=1)
        if type == "mount":
            combine.append(
                "{}=bucket:{}/{}".format(path, bucket_name, volume_config["mount"][key])
            )
        elif type == "crypt":
            combine.append("{}=crypt-{}-{}:".format(path, bucket_name, key))
    input_dict["combine"] = {"type": "combine", "upstreams": " ".join(combine)}
    return input_dict


output_config = {
    "name": "rclone-config",
    "path": "{}.conf".format(get_logical_name("rclone")),
    "input_fn": input_fn,
}
