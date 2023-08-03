import json

from pulumi import ComponentResource, ResourceOptions

from _common import service_config
from _container import DockerContainer
from _service import ntfy
from _service.resource import child_opts

_telegram_config = service_config["telegram"]


class TelegramLoginCode(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Telegram", "login-code", None, child_opts)
        self.__container = DockerContainer.build(
            "telegram-login-code",
            opts=ResourceOptions(parent=self),
            command=["login_code.py"],
            image="telegram",
            envs={"TELEGRAM_CONFIG": json.dumps(_telegram_config)} | ntfy.env,
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


telegram_login_code = TelegramLoginCode()
