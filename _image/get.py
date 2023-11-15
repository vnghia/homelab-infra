import os

import docker


def main():
    repository = os.environ["IMAGE_REPOSITORY"]
    tag = os.environ["IMAGE_TAG"]
    image = docker.from_env().images.pull(
        repository=repository, tag=tag, platform=os.environ["IMAGE_PLATFORM"]
    )
    print(image.id)


if __name__ == "__main__":
    main()
