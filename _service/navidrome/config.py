from _common import navidrome_config
from _secret import secret

output_config = {
    "name": "navidrome-config",
    "volume": navidrome_config["data"]["volume"],
    "path": "navidrome.toml",
    "input": {
        "MusicFolder": navidrome_config["music"]["dir"],
        "DataFolder": navidrome_config["data"]["dir"],
        "LogLevel": "info",
        "PasswordEncryptionKey": secret.keys["navidrome-encryption"].result,
        "ScanSchedule": "@every 24h",
        "Spotify.ID": navidrome_config["spotify"]["id"],
        "Spotify.Secret": navidrome_config["spotify"]["secret"],
        "SubsonicArtistParticipations": True,
        "TranscodingCacheSize": "1GB",
        "EnableSharing": True,
    },
}