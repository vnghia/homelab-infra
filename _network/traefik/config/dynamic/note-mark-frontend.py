from pulumi import Output

from _common import service_config
from _network.dns.hostnames import hostnames

_note_mark_config = service_config["note-mark"]

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "note-mark-frontend",
            "rule": Output.format("Host(`{0}`)", hostnames["private-note-mark"]),
        },
        "service": {"port": _note_mark_config["port"]},
    }
}
