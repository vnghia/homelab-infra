import base64
import random

from Crypto.Cipher import AES
from pulumi import ResourceOptions

from _common import get_logical_name, storage_config, volume_config
from _secret import secret


def rclone_obscure(plaintext: str):
    random.seed(0)
    iv = random.randbytes(AES.block_size)

    crypt_key = b"\x9c\x93\x5b\x48\x73\x0a\x55\x4d\x6b\xfd\x7c\x63\xc8\x86\xa9\x2b\xd3\x90\x19\x8e\xb8\x12\x8a\xfb\xf4\xde\x16\x2b\x8b\x95\xf6\x38"
    crypter = AES.new(key=crypt_key, mode=AES.MODE_CTR, initial_value=iv, nonce=b"")
    encrypted_password = crypter.encrypt(plaintext.encode())

    return base64.urlsafe_b64encode(iv + encrypted_password).decode("utf-8").rstrip("=")


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
        password_obscured = password.result.apply(rclone_obscure)
        salt = secret.build_password("crypt-{}-salt".format(name), opts=opts, length=32)
        salt_obscured = salt.result.apply(rclone_obscure)

        input_dict["crypt-{}-{}".format(bucket_name, name)] = {
            "type": "crypt",
            "remote": "bucket:{}/{}".format(bucket_name, prefix),
            "password": password_obscured,
            "password2": salt_obscured,
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
    if combine:
        input_dict["combine"] = {"type": "combine", "upstreams": " ".join(combine)}
    return input_dict


output_config = {
    "name": "rclone-config",
    "path": "{}.conf".format(get_logical_name("rclone")),
    "input_fn": input_fn,
}
