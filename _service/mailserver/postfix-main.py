from _common import container_storage_config

_mailserver_volume = container_storage_config["mailserver"]


output_config = {
    "type": "raw",
    "name": "mailserver-postfix-main",
    "volume": _mailserver_volume["config"]["volume"],
    "path": "postfix-main.cf",
    "input": "smtp_tls_security_level = may",
}
