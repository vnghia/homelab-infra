from _service.authelia.authelia import authelia
from _service.dozzle.dozzle import dozzle
from _service.immich.immich import immich
from _service.jellyfin.jellyfin import jellyfin
from _service.linkwarden.linkwarden import linkwarden
from _service.mailserver.mainserver import mailserver
from _service.memos.memos import memos
from _service.monica.monica import monica
from _service.navidrome.navidrome import navidrome
from _service.ntfy.ntfy import ntfy
from _service.paperless_ngx.paperless_ngx import paperless_ngx
from _service.password_storage.password_storage import password_storage
from _service.script_server.script_server import script_server
from _service.slskd.slskd import slskd
from _service.syncthing.syncthing import syncthing
from _service.telegram.login_code import telegram_login_code
from _service.ttyd.ttyd import ttyd
from _service.webdav_storage.webdav_storage import webdav_storage

__all__ = [
    "authelia",
    "dozzle",
    "immich",
    "jellyfin",
    "linkwarden",
    "mailserver",
    "memos",
    "monica",
    "navidrome",
    "ntfy",
    "paperless_ngx",
    "password_storage",
    "rclone_webdav",
    "script_server",
    "slskd",
    "syncthing",
    "telegram_login_code",
    "ttyd",
    "webdav_storage",
]
