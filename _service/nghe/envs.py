import binascii

from _common import service_config
from _data.postgres import postgres
from _secret import secret
from _common import storage_config

_aws_env = storage_config["aws"]
_nghe_config = service_config["nghe"]
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
    "NGHE_SCAN__CHANNEL_SIZE": 50,
    "NGHE_SCAN__POOL_SIZE": 50,
    "NGHE_S3__ENABLE": "true",
    "AWS_REGION": "auto",
} | _aws_env
