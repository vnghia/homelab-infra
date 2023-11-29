from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "monica",
            "rule": Output.format("Host(`{0}`)", hostnames["private-monica"]),
            "middlewares": ["rewrite-redirect-https", "monica-headers"],
        },
        "service": {"port": 80},
        "middleware": {
            "monica-headers": {
                "name": "headers",
                "customResponseHeaders": {"WWW-Authenticate": 'Basic realm="monica"'},
            }
        },
    }
}
