from _common import get_logical_name, storage_config

output_config = {
    "name": "rclone-config",
    "path": "{}.conf".format(get_logical_name("rclone")),
    "input": {
        "bucket": {
            "type": "s3",
            "provider": "Other",
            "region": storage_config["region"],
            "access_key_id": storage_config["key-id"],
            "secret_access_key": storage_config["key-secret"],
            "endpoint": storage_config["endpoint"],
        }
    },
}
