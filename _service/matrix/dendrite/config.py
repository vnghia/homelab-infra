import os
from pathlib import Path

from pulumi import Output

from _common import container_storage_config, service_config
from _data.postgres import postgres
from _network.dns.hostnames import hostnames
from _secret import secret
from _service.matrix.dendrite.key import output_config as _key_config

_postgres_config = postgres.db["dendrite"]
_dendrite_volume = container_storage_config["dendrite"]

_matrix_config = service_config["matrix"]
_dendrite_url = hostnames["public-dendrite"]

output_config = {
    "type": "yaml",
    "name": "dendrite-config",
    "volume": _dendrite_volume["config"]["volume"],
    "path": "dendrite.yaml",
    "input": {
        "version": 2,
        "global": {
            "server_name": _matrix_config["server-name"],
            "private_key": os.fspath(
                Path(_dendrite_volume["config"]["dir"]) / _key_config["path"]
            ),
            "database": {
                "connection_string": Output.format(
                    "postgresql://{0}:{1}@{2}:{3}/{4}?sslmode=disable",
                    _postgres_config["username"],
                    _postgres_config["password"],
                    _postgres_config["host"],
                    _postgres_config["port"],
                    _postgres_config["database"],
                ),
            },
            "well_known_server_name": "{}:443".format(_dendrite_url),
            "well_known_client_name": "https://{}".format(_dendrite_url),
            "well_known_sliding_sync_proxy": "https://{}".format(
                hostnames["public-sliding-sync"]
            ),
            "disable_federation": True,
            "presence": {"enable_inbound": False, "enable_outbound": False},
        },
        "client_api": {
            "registration_shared_secret": secret.keys[
                "dendrite-registration-secret"
            ].result
        },
        "media_api": {
            "base_path": _dendrite_volume["media"]["dir"],
            "max_file_size_bytes": 104857600,  # 100 MiB
        },
        "sync_api": {
            "real_ip_header": "X-Real-IP",
            "search": {
                "enabled": True,
                "index_path": _dendrite_volume["searchindex"]["dir"],
            },
        },
        "jetstream": {"storage_path": _dendrite_volume["jetstream"]["dir"]},
    },
}
