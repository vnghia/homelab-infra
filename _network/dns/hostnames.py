from _common import dns_config


def __build_record_info():
    records = {}
    hostnames = {}
    for zone, zone_config in dns_config["zone"].items():
        zone_key = zone_config.pop("key", zone)
        for ip_type in ["public", "private"]:
            for record_key, name in zone_config.get(ip_type, {}).items():
                full_key = "-".join(
                    ([zone_key] if zone_key != "main" else [])
                    + [ip_type]
                    + [record_key]
                )
                is_apex = name == "@"
                hostname = "{}{}{}".format(
                    "" if is_apex else name, "" if is_apex else ".", zone
                )
                records[full_key] = {
                    "type": ip_type,
                    "zone": zone,
                    "name": name,
                    "hostname": hostname,
                }
                hostnames[full_key] = hostname

    return records, hostnames


records, hostnames = __build_record_info()
