from _service.dozzle.dozzle import dozzle
from _service.navidrome.navidrome import navidrome
from _service.ntfy.ntfy import ntfy
from _service.rclone.rclone_webdav import rclone_webdav
from _service.script_server.script_server import script_server
from _service.syncthing.syncthing import syncthing
from _service.ttyd.ttyd import ttyd

__all__ = [
    "dozzle",
    "navidrome",
    "ntfy",
    "rclone_webdav",
    "script_server",
    "syncthing",
    "ttyd",
]
