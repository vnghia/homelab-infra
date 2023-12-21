from _common import get_logical_name, service_config
from _secret import secret

_crowdsec_config = service_config["crowdsec"]

envs = {
    "COLLECTIONS": " ".join(["crowdsecurity/traefik", "LePresidente/authelia"]),
    "CUSTOM_HOSTNAME": "crowdsec",
    "ENROLL_KEY": _crowdsec_config["console-id"],
    "ENROLL_INSTANCE_NAME": get_logical_name(),
    "USE_WAL": "true",
    "BOUNCER_KEY_TRAEFIK": secret.keys["crowdsec-traefik-bouncer"].result,
}
