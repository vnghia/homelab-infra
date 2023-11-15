from _common.naming import get_logical_name


def gen_postgres_backup_restore_script(service_name: str):
    return {
        "path": ["{}.dump".format(service_name)],
        "backup-script": {
            "pre": [
                [
                    "docker",
                    "exec",
                    get_logical_name("postgres-{}".format(service_name)),
                    "pg_dump",
                    "-Fc",
                    "-U",
                    service_name,
                    "-w",
                    "-d",
                    service_name,
                    "-f",
                    "/backup/{}.dump".format(service_name),
                ]
            ]
        },
        "restore-script": {
            "post": [
                [
                    "docker",
                    "exec",
                    get_logical_name("postgres-{}".format(service_name)),
                    "pg_restore",
                    "-U",
                    service_name,
                    "-w",
                    "-d",
                    service_name,
                    "--clean",
                    "/backup/{}.dump".format(service_name),
                ]
            ]
        },
    }
