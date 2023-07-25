import os

import httpx


def main():
    TAILSCALE_API_KEY = os.environ["TAILSCALE_API_KEY"]
    TAILSCALE_TAILNET = os.environ["TAILSCALE_TAILNET"]
    TAILSCALE_DEVICE_HOSTNAME = os.environ["TAILSCALE_DEVICE_HOSTNAME"]

    client = httpx.Client(
        headers={"Authorization": "Bearer {}".format(TAILSCALE_API_KEY)}
    )

    list_res = client.get(
        "https://api.tailscale.com/api/v2/tailnet/{}/devices?fields=default".format(
            TAILSCALE_TAILNET
        )
    )
    list_res.raise_for_status()

    device_ids = [
        device["id"]
        for device in list_res.json()["devices"]
        if device["hostname"] == TAILSCALE_DEVICE_HOSTNAME
    ]
    for device_id in device_ids:
        del_res = client.delete(
            "https://api.tailscale.com/api/v2/device/{}".format(device_id)
        )
        del_res.raise_for_status()


if __name__ == "__main__":
    main()
