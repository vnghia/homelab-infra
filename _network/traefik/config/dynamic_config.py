from pathlib import Path

import deepmerge
from pulumi import ComponentResource, ResourceOptions

from _common import container_storage_config, service_config
from _file import Template

_traefik_config = service_config["traefik"]
_traefik_volume = container_storage_config["traefik"]


class TraefikDynamicConfig(ComponentResource):
    def __init__(self, opts: ResourceOptions) -> None:
        super().__init__("traefik:dynamic:Configuration", "dynamic", None, opts)

        self.__child_opts = ResourceOptions(parent=self)
        self.__toml_file = Template(self.__child_opts, self.__build_toml_middleware)
        self.dynamic_config = {}

        for module_path in (Path(__file__).parent / "dynamic").glob("*.py"):
            output_path = module_path.with_suffix(".toml").name
            self.dynamic_config[module_path.stem] = self.__toml_file.build(
                module_path=module_path,
                config={
                    "name": "traefik-{}".format(module_path.stem),
                    "volume": _traefik_volume["config"]["volume"],
                    "path": output_path,
                    "schema": _traefik_config["schema"]["dynamic"],
                },
            )

        self.register_outputs({k: v["content"] for k, v in self.dynamic_config.items()})

    def __build_toml_middleware(self, input, _):
        main_type = input.pop("type")
        is_http = main_type == "http"

        root_dict = {}
        main_dict = {}

        router_config = input.pop("router", None)
        if router_config:
            router_dict = {}

            router_name = router_config.pop("name")
            router_service = router_config.pop("service", router_name)
            router_dict["service"] = router_service

            if is_http:
                router_dict["tls"] = {"certResolver": "leresolver_dns"}
                sec_mode = router_config.pop("sec_mode", "private")
                if sec_mode == "private":
                    router_dict["entryPoints"] = ["https-private"]
                elif sec_mode == "public":
                    router_dict["entryPoints"] = ["https-public"]
                    router_dict["middlewares"] = router_config.pop("middlewares", [])
                    router_dict["middlewares"].append("crowdsec")
                else:
                    router_dict["entryPoints"] = ["https-public"]

            main_dict["routers"] = {
                router_name: deepmerge.always_merger.merge(router_dict, router_config)
            }

            router_service_config = input.pop("service", None)
            if router_service_config:
                service_name = router_service_config.pop("name", None) or router_service
                service_protocol = router_service_config.pop(
                    "protocol", "http" if is_http else ""
                )
                service_host = router_service_config.pop("host", service_name)
                service_port = router_service_config.pop("port", "")
                service_url = "{}{}{}{}{}".format(
                    service_protocol,
                    "://" if service_protocol else "",
                    service_host,
                    ":" if service_port else "",
                    service_port,
                )

                router_service_dict = {
                    "loadBalancer": {
                        "servers": [{"url" if is_http else "address": service_url}]
                    }
                }
                main_dict["services"] = {
                    service_name: deepmerge.always_merger.merge(
                        router_service_dict, router_service_config
                    )
                }

        middleware_configs = input.pop("middleware", None)
        if middleware_configs:
            middlewares_dict = {}

            for middleware_key, middleware_config in middleware_configs.items():
                middleware_dict = {}

                middleware_name = middleware_config.pop("name")
                middleware_plugin = middleware_config.pop("plugin", False)
                if middleware_plugin:
                    middleware_dict["plugin"] = {middleware_name: middleware_config}
                else:
                    middleware_dict[middleware_name] = middleware_config

                middlewares_dict[middleware_key] = middleware_dict

            main_dict["middlewares"] = middlewares_dict

        if len(main_dict):
            root_dict[main_type] = main_dict

        return deepmerge.always_merger.merge(root_dict, input)
