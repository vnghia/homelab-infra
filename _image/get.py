import os

import docker


def main():
    registry_data = docker.from_env().images.get_registry_data(os.environ["IMAGE_NAME"])
    print(registry_data.pull(os.environ["IMAGE_PLATFORM"]).id)


if __name__ == "__main__":
    main()
