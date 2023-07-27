from pulumi import Output

from _network.dns import hostnames

output_config = {
    "input": {
        "type": "http",
        "router": {
            "name": "rclone-webdav",
            "rule": Output.format("Host(`{0}`)", hostnames["public-rclone"]),
            "sec_mode": "public",
        },
        "service": {"port": 8080},
    }
}
