import base64
import os
from pathlib import Path

from _common import container_storage_config, service_config
from _network.dns.hostnames import hostnames
from _secret import secret

_note_mark_config = service_config["note-mark"]
_note_mark_backend_volume = container_storage_config["note-mark-backend"]

_note_mark_data_dir = Path(_note_mark_backend_volume["data"]["dir"])

envs = {
    "BIND__PORT": _note_mark_config["port"],
    "DB__TYPE": "sqlite",
    "DB__URI": os.fspath(_note_mark_data_dir / "note-mark.sqlite"),
    "JWT_SECRET": secret.keys["note-mark-jwt"].result.apply(
        lambda x: base64.b64encode(x.encode()).decode()
    ),
    "DATA_PATH": os.fspath(_note_mark_data_dir),
    "CORS_ORIGINS": "https://{}".format(hostnames["private-note-mark"]),
}
