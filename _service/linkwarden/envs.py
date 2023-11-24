from pulumi import Output

from _data.postgres import postgres
from _network.dns.hostnames import hostnames
from _secret import secret

_postgres_config = postgres.db["linkwarden"]

envs = {
    "NEXTAUTH_SECRET": secret.build_string("linkwarden-secret", length=32).result,
    "DATABASE_URL": Output.format(
        "postgresql://{0}:{1}@{2}:{3}/{4}",
        _postgres_config["username"],
        _postgres_config["password"],
        _postgres_config["host"],
        _postgres_config["port"],
        _postgres_config["database"],
    ),
    "NEXTAUTH_URL": "https://{}".format(hostnames["private-linkwarden"]),
    "NEXT_PUBLIC_DISABLE_REGISTRATION": True,
}
