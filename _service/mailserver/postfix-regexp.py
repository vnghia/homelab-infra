from pulumi import Output

from _common import container_storage_config, service_config
from _network.dns.hostnames import hostnames
from _service.ntfy.ntfy import ntfy

_mailserver_volume = container_storage_config["mailserver"]
_ntfy_config = service_config["ntfy"]


output_config = {
    "type": "raw",
    "name": "mailserver-postfix-regexp",
    "volume": _mailserver_volume["config"]["volume"],
    "path": "postfix-regexp.cf",
    "input": Output.all(
        *[
            Output.format(
                "/.*@{0}/ {1}",
                hostnames[hostname],
                ntfy.build_to_email(service),
            )
            for service, hostname in _ntfy_config["email-server"]
            .get("service", {})
            .items()
        ]
    ).apply(lambda args: "\n".join(args)),
}
