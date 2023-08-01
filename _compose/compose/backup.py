from pathlib import Path

from _common import backup_config
from _data.backup.restic.restic import restic_repo
from _image import docker_image


def input_fn():
    input_dict = {
        "services": {
            "backup": {
                "image": docker_image.image_map["backup"]["image_id"],
                "pull_policy": "never",
                "profiles": ["manual"],
                "environment": restic_repo.env
                | {"RESTIC_CACHE_DIR": backup_config["cache"]["dir"]}
                | {"BACKUP_CONFIG": backup_config},
            }
        },
    }

    volume_dict = {}
    backup_prefix = Path(backup_config["common"]["prefix"])
    for cs in backup_config["service"].values():
        for kv in cs.get("volume", {}).keys():
            volume_dict[str(backup_prefix / kv)] = {"volume": kv}
    volume_dict["/var/run/docker.sock"] = {}
    volume_dict[backup_config["cache"]["dir"]] = {
        "volume": backup_config["cache"]["volume"]
    }
    input_dict["services"]["backup"]["volumes"] = volume_dict

    return input_dict


output_config = {
    "input": input_fn(),
}
