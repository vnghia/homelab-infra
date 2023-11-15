import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from _common import service_config
from _container import DockerContainer
from _network.traefik import traefik_proxy
from _service.resource import child_opts

_ttyd_config = service_config["ttyd"]


class Ttyd(ComponentResource):
    def __init__(self) -> None:
        super().__init__("service:index:Ttyd", "ttyd", None, child_opts)
        self.__child_opts = ResourceOptions(parent=self)

        ttyd_command = [
            "ttyd",
            "-p",
            _ttyd_config["port"],
            "--writable",
            "--base-path",
            "{}".format(_ttyd_config["base-path"]),
        ]
        for k, v in _ttyd_config["option"].items():
            ttyd_command += ["-t", "{}={}".format(k, v)]
        ttyd_command += ["bash"]

        self.__container = DockerContainer.build(
            "ttyd",
            command=ttyd_command,
            opts=self.__child_opts.merge(
                ResourceOptions(
                    depends_on=[traefik_proxy.dynamic_config["ttyd"]["file"]]
                )
            ),
            hosts=[
                docker.ContainerHostArgs(host="host.docker.internal", ip="host-gateway")
            ],
            pid_mode="host",
            privileged=True,
            volumes={"/var/run/docker.sock": {}},
        )
        self.container_id = self.__container.id
        self.register_outputs({"container_id": self.container_id})


ttyd = Ttyd()
