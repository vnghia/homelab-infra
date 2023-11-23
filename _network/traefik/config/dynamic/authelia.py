from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "authelia",
            "rule": Output.format("Host(`{0}`)", hostnames["public-authelia"]),
            "sec_mode": "public",
        },
        "service": {"port": 9091},
        "middleware": {
            "authelia-forward-auth": {
                "name": "forwardAuth",
                "address": "http://authelia:9091/api/authz/forward-auth",
                "trustForwardHeader": True,
                "authResponseHeaders": [
                    "Authorization",
                    "Proxy-Authorization",
                    "Remote-User",
                    "Remote-Groups",
                    "Remote-Email",
                    "Remote-Name",
                ],
            }
        },
    }
}
