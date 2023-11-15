from _common.config import container_storage_config
from _common.naming import get_logical_name

_paperless_ngx_volume = container_storage_config["paperless-ngx"]

script_config = {
    "backup-script": {
        "pre": [
            [
                "docker",
                "exec",
                get_logical_name("paperless-ngx"),
                "document_exporter",
                _paperless_ngx_volume["export"]["dir"],
                "-c",
                "-d",
                "-f",
                "-p",
                "-sm",
            ]
        ]
    },
    "restore-script": {
        "post": [
            [
                "docker",
                "exec",
                get_logical_name("paperless-ngx"),
                "document_importer",
                _paperless_ngx_volume["export"]["dir"],
            ]
        ]
    },
}
