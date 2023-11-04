from _service.dozzle.dozzle import dozzle
from _service.immich.immich import immich
from _service.jellyfin.jellyfin import jellyfin
from _service.memos.memos import memos
from _service.navidrome.navidrome import navidrome
from _service.ntfy.ntfy import ntfy
from _service.paperless_ngx.paperless_ngx import paperless_ngx
from _service.rclone.rclone_webdav import rclone_webdav
from _service.script_server.script_server import script_server
from _service.slskd.slskd import slskd
from _service.syncthing.syncthing import syncthing
from _service.telegram.login_code import telegram_login_code
from _service.ttyd.ttyd import ttyd

__all__ = [
    "dozzle",
    "immich",
    "jellyfin",
    "memos",
    "navidrome",
    "ntfy",
    "paperless_ngx",
    "rclone_webdav",
    "script_server",
    "slskd",
    "syncthing",
    "telegram_login_code",
    "ttyd",
]
