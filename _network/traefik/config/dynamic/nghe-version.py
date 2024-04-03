from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "nghe-version",
            "rule": Output.format("Host(`{0}`) && PathPrefix(`/rest/ping.view`)", hostnames["public-nghe"]),
            "sec_mode": "public",
            "service": "navidrome@file",
        },
    }
}
