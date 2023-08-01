from pathlib import Path

from pulumi import ComponentResource, ResourceOptions

from _command import Command
from _common import aws, storage_config
from _data.resource import child_opts
from _image import docker_image
from _secret import secret

_aws_env = storage_config["aws"]


class ResticRepo(ComponentResource):
    def __init__(self) -> None:
        super().__init__("data:backup:Restic", "Restic", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        self.__repo_prefix = "backup/restic"
        self.__repo_password = secret.build_password(
            "restic-repo-password",
            opts=self.__child_opts,
            export=True,
        )
        self.password = self.__repo_password.result

        self.__repo_cleanup = aws.build_cleanup(
            "restic-repo-cleanup",
            opts=self.__child_opts,
            prefix=self.__repo_prefix,
            triggers=[self.password],
        )

        self.__repo_init = Command.build(
            "restic-repo-init",
            opts=self.__child_opts.merge(
                ResourceOptions(depends_on=self.__repo_cleanup)
            ),
            create=Path(__file__).parent / "init.py",
            update="",
            environment={
                "RESTIC_IMAGE_ID": docker_image.image_map["restic"]["image_id"],
                "RESTIC_PASSWORD": self.password,
                "RESTIC_REPO_PREFIX": self.__repo_prefix,
            }
            | _aws_env,
        )

        self.repo = self.__repo_init.stdout
        self.env = {
            "RESTIC_REPOSITORY": self.repo,
            "RESTIC_PASSWORD": self.password,
        } | _aws_env
        self.register_outputs({"repo": self.repo, "password": self.password})


restic_repo = ResticRepo()
