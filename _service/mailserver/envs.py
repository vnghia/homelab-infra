from pulumi import Output

from _network.dns.hostnames import hostnames
from _service.ntfy.ntfy import ntfy

envs = {
    "OVERRIDE_HOSTNAME": hostnames["private-mailserver"],
    "ONE_DIR": 1,
    "ACCOUNT_PROVISIONER": "FILE",
    "ENABLE_UPDATE_CHECK": 0,
    "PERMIT_DOCKER": "network",
    "POSTFIX_INET_PROTOCOLS": "ipv4",
    "SPOOF_PROTECTION": 0,
    "ENABLE_SRS": 0,
    "ENABLE_OPENDKIM": 0,
    "ENABLE_OPENDMARC": 0,
    "ENABLE_POLICYD_SPF": 0,
    "ENABLE_POP3": 0,
    "ENABLE_CLAMAV": 0,
    "ENABLE_RSPAMD": 0,
    "ENABLE_AMAVIS": 0,
    "ENABLE_DNSBL": 0,
    "ENABLE_FAIL2BAN": 0,
    "ENABLE_MANAGESIEVE": 0,
    "ENABLE_SPAMASSASSIN": 0,
    "ENABLE_FETCHMAIL": 0,
    "ENABLE_POSTGREY": 0,
    "ENABLE_SASLAUTHD": 0,
    "SMTP_ONLY": 1,
    "SSL_TYPE": "letsencrypt",
    "SSL_DOMAIN": hostnames["private-mailserver"],
    "DEFAULT_RELAY_HOST": Output.format(
        "[{0}]:{1}", ntfy.smtp_env["NTFY_SMTP_SERVER"], ntfy.smtp_env["NTFY_SMTP_PORT"]
    ),
}
