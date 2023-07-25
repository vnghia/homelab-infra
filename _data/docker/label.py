import pulumi_docker as docker

from _common import constant

DOCKER_VOLUME_LABELS = [
    docker.VolumeLabelArgs(label=k, value=v) for k, v in constant.PROJECT_TAG.items()
]
