import os

import docker


def main():
    plugin = docker.from_env().plugins.get(os.environ["PLUGIN_NAME"])
    if plugin.enabled:
        plugin.disable()


if __name__ == "__main__":
    main()
