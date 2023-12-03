from _service.authelia.authelia import authelia
from _service.central_storage.central_storage import central_storage
from _service.dozzle.dozzle import dozzle
from _service.immich.immich import immich
from _service.jellyfin.jellyfin import jellyfin
from _service.linkwarden.linkwarden import linkwarden
from _service.mailserver.mailserver import mailserver
from _service.meilisearch.meilisearch import meilisearch
from _service.monica.monica import monica
from _service.navidrome.navidrome import navidrome
from _service.ntfy.ntfy import ntfy
from _service.paperless_ngx.paperless_ngx import paperless_ngx
from _service.password_storage.password_storage import password_storage
from _service.ryot.ryot import ryot
from _service.script_server.script_server import script_server
from _service.slskd.slskd import slskd
from _service.syncthing.syncthing import syncthing
from _service.telegram.login_code import telegram_login_code
from _service.ttyd.ttyd import ttyd

__all__ = [
    "authelia",
    "central_storage",
    "dozzle",
    "immich",
    "jellyfin",
    "linkwarden",
    "mailserver",
    "meilisearch",
    "monica",
    "navidrome",
    "ntfy",
    "paperless_ngx",
    "password_storage",
    "ryot",
    "script_server",
    "slskd",
    "syncthing",
    "telegram_login_code",
    "ttyd",
]
