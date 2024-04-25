import binascii

from _common import container_storage_config, service_config
from _data.postgres import postgres
from _secret import secret

_nghe_config = service_config["nghe"]
_nghe_volume = container_storage_config["nghe"]
_postgres_config = postgres.db["nghe"]

envs = {
    "NGHE_SERVER__PORT": 3000,
    "NGHE_DATABASE__KEY": secret.keys["nghe-encryption"].result.apply(
        lambda x: binascii.hexlify(x.encode()).decode("ascii")
    ),
    "NGHE_DATABASE__URL": _postgres_config["url"],
    "NGHE_LASTFM__KEY": _nghe_config["lastfm"]["key"],
    "NGHE_SPOTIFY__ID": _nghe_config["spotify"]["id"],
    "NGHE_SPOTIFY__SECRET": _nghe_config["spotify"]["secret"],
}
