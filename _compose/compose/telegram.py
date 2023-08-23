from _common import service_config
from _image import docker_image
from _service import ntfy

_telegram_config = service_config["telegram"]


def input_fn():
    input_dict = {"services": {}}

    for script in ["login", "refresh_session"]:
        input_dict["services"][script] = {
            "image": docker_image.image_map["telegram"]["image_id"],
            "command": ["{}.py".format(script)],
            "pull_policy": "never",
            "profiles": ["manual"],
            "environment": {"TELEGRAM_CONFIG": _telegram_config} | ntfy.env,
            "volumes": {_telegram_config["session"]: {"volume": "telegram-session"}},
        }

    return input_dict


output_config = {"input": input_fn()}
