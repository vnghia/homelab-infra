from _common import container_storage_config
from _secret import secret

_slskd_volume = container_storage_config["slskd"]

envs = {
    "SLSKD_SHARED_DIR": _slskd_volume["music"]["dir"],
    "SLSKD_SLSK_USERNAME": secret.accounts["soulseek"]["username"],
    "SLSKD_SLSK_PASSWORD": secret.accounts["soulseek"]["password"],
    "SLSKD_SLSK_CONNECTION_TIMEOUT": 10000,
    "SLSKD_SLSK_LISTEN_PORT": 50300,
    "SLSKD_NO_HTTPS": True,
    "SLSKD_NO_AUTH": True,
}
