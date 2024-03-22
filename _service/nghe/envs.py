import binascii

from _common import container_storage_config
from _data.postgres import postgres
from _secret import secret

_nghe_volume = container_storage_config["nghe"]
_postgres_config = postgres.db["nghe"]

envs = {
    "NGHE_SERVER__HOST": "::",
    "NGHE_SERVER__PORT": 3000,
    "NGHE_DATABASE__KEY": secret.keys["nghe-encryption"].result.apply(
        lambda x: binascii.hexlify(x.encode()).decode("ascii")
    ),
    "NGHE_DATABASE__URL": _postgres_config["url"],
    "NGHE_FOLDER__TOP_PATHS": str([_nghe_volume["music-self"]["dir"]]).replace(
        "'", '"'
    ),
    "NGHE_SCAN__CHANNEL_SIZE": 1000,
    "RUST_LOG": "nghe=trace,tower_http=trace",
}
