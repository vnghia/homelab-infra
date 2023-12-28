from pulumi import Output

from _common import storage_config
from _data.postgres import postgres
from _network.dns.hostnames import hostnames
from _secret import secret

_postgres_config = postgres.db["linkwarden"]

envs = {
    "NEXTAUTH_SECRET": secret.keys["linkwarden-secret"].result,
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
    "SPACES_KEY": storage_config["key-id"],
    "SPACES_SECRET": storage_config["key-secret"],
    "SPACES_ENDPOINT": storage_config["endpoint"],
    "SPACES_REGION": storage_config["region"],
    "SPACES_BUCKET_NAME": storage_config["bucket"],
}
