from pulumi import Output


def input_fn(_, args: dict):
    content = Output.all(**args).apply(
        lambda args: "\n".join(
            [
                "bind 0.0.0.0 -::1",
                "port {}".format(args["port"]),
                "protected-mode no",
                "requirepass {}".format(args["password"]),
                "daemonize no",
                "loglevel notice",
                'logfile ""',
                "save 3600 1 300 100 60 10000",
            ]
        )
    )
    return content


output_config = {"path": "/etc/redis/redis.conf", "type": "raw", "input_fn": input_fn}
