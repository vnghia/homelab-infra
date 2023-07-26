import os

import docker


def main():
    plugin = docker.from_env().plugins.get(os.environ["PLUGIN_NAME"])
    if plugin.enabled:
        plugin.disable()
    plugin.configure(
        {
            "args": "--allow-other --config={} --vfs-cache-mode=full -v".format(
                os.environ["RCLONE_CONFIG"]
            ),
        }
    )
    plugin.enable()


if __name__ == "__main__":
    main()
