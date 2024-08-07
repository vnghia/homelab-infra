from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "nhac",
            "service": "nghe",
            "rule": Output.format("Host(`{0}`)", hostnames["private-nhac"]),
            "sec_mode": "private",
        },
        "service": {"port": 3000},
    }
}
