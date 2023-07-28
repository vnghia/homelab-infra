from _common import container_storage_config, service_config
from _secret import secret

_navidrome_config = service_config["navidrome"]
_navidrome_volume = container_storage_config["navidrome"]

output_config = {
    "name": "navidrome-config",
    "volume": _navidrome_volume["data"]["volume"],
    "path": "navidrome.toml",
    "input": {
        "MusicFolder": _navidrome_volume["music"]["dir"],
        "DataFolder": _navidrome_volume["data"]["dir"],
        "LogLevel": "info",
        "PasswordEncryptionKey": secret.keys["navidrome-encryption"].result,
        "ScanSchedule": "@every 24h",
        "Spotify.ID": _navidrome_config["spotify"]["id"],
        "Spotify.Secret": _navidrome_config["spotify"]["secret"],
        "SubsonicArtistParticipations": True,
        "TranscodingCacheSize": "1GB",
        "EnableSharing": True,
    },
}
