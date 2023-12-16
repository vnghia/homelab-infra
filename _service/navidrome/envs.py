from _common import container_storage_config, service_config
from _secret import secret

_navidrome_config = service_config["navidrome"]
_navidrome_volume = container_storage_config["navidrome"]

envs = {
    "ND_MUSICFOLDER": _navidrome_volume["music"]["dir"],
    "ND_DATAFOLDER": _navidrome_volume["data"]["dir"],
    "ND_LOGLEVEL": "info",
    "ND_PASSWORDENCRYPTIONKEY": secret.keys["navidrome-encryption"].result,
    "ND_SCANSCHEDULE": "0",
    "ND_SPOTIFY_ID": _navidrome_config["spotify"]["id"],
    "ND_SPOTIFY_SECRET": _navidrome_config["spotify"]["secret"],
    "ND_SUBSONICARTISTPARTICIPATIONS": True,
    "ND_TRANSCODINGCACHESIZE": "1GB",
    "ND_ENABLESHARING": True,
    "ND_IMAGECACHESIZE": "1GB",
}
