from pulumi import Output

from _common import storage_config
from _data.postgres import postgres

_postgres_config = postgres.db["ryot"]

envs = {
    "DATABASE_URL": Output.format(
        "postgresql://{0}:{1}@{2}:{3}/{4}",
        _postgres_config["username"],
        _postgres_config["password"],
        _postgres_config["host"],
        _postgres_config["port"],
        _postgres_config["database"],
    ),
    "FILE_STORAGE_S3_ACCESS_KEY_ID": storage_config["key-id"],
    "FILE_STORAGE_S3_SECRET_ACCESS_KEY": storage_config["key-secret"],
    "FILE_STORAGE_S3_URL": storage_config["endpoint"],
    "FILE_STORAGE_S3_REGION": storage_config["region"],
    "FILE_STORAGE_S3_BUCKET_NAME": storage_config["bucket"],
}
