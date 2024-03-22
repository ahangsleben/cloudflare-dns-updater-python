import argparse
import configparser
import ipaddress

import requests


def parse_arguments():
    """
    Read in config file path from command line arguments.

    :returns: User input path to the config file.
    :rtype: string
    """

    parser = argparse.ArgumentParser(
        description="Updates a Cloudflare domain name DNS A-Record to the public IP address where this script was run."
    )
    parser.add_argument(
        "-c", "--config", help="Path to the config file.", default="config.ini"
    )

    arguments = parser.parse_args()
    return arguments.config


def read_config_file(config_file_path):
    """
    Reads in the config file that specifies the Cloudflare secrets and domain name to
    update.

    :param string config_file_path: Path to the config file.
    :returns: Cloudflare Zone ID, API token, and domain name.
    :rtype: Tuple[string, string, string]
    """

    config = configparser.ConfigParser()
    config.read(config_file_path)
    if "cloudflare" not in config:
        raise Exception("[cloudflare] section not found in config file.")

    input_config = config["cloudflare"]
    for field in ("zone_id", "api_token", "domain_name"):
        if field not in input_config:
            raise Exception(f"Required field {field} not found in config.")

    return (
        input_config["zone_id"],
        input_config["api_token"],
        input_config["domain_name"],
    )


def get_current_public_ip():
    """
    Determines the current public IP address of wherever this script is running.

    :returns: Public IP of the current computer.
    :rtype: string
    """

    url = "https://ifconfig.me/ip"

    response = requests.get(url)
    ip = response.text

    # Validate IP address. Raises a ValueError if the IP isn't valid.
    ipaddress.ip_address(ip)

    return ip


def update_cloudflare_dns_entry(zone_id, api_token, domain_name, ip_address):
    """
    Updates a Cloudflare Domain Name A-Record with the given IP Address.

    :param string zone_id: Cloudflare API key.
    :param string api_token: Cloudflare API key secret.
    :param string domain_name: Domain name to update.
    :param string ip_address: IP address to set in A-Record.
    """

    list_zone_records_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

    headers = {
        "Authorization": f"Bearer {api_token}",
    }

    params = {
        "name": domain_name,
        "type": "A",
    }

    response = requests.get(list_zone_records_url, headers=headers, params=params)
    response.raise_for_status()

    domain_records = response.json()["result"]
    if len(domain_records) != 1:
        print(
            f"Expected one domain record for '{domain_name}', but found {len(domain_records)}"
        )
        return

    domain_record = domain_records[0]
    current_cloudflare_ip = domain_record["content"]
    if current_cloudflare_ip == ip_address:
        print("IP already up to date.")
        return

    record_id = domain_record["id"]
    update_zone_record_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"

    payload = {
        "content": ip_address,
        "name": domain_name,
        "type": "A",
    }

    response = requests.patch(update_zone_record_url, headers=headers, json=payload)
    if not response.ok:
        print("Failed to update IP.")

    print("Successfully updated IP.")


def main():
    """
    Updates the Cloudflare domain name with the current public IP address.
    """

    config_file_path = parse_arguments()
    zone_id, api_token, domain_name = read_config_file(config_file_path)
    public_ip = get_current_public_ip()

    update_cloudflare_dns_entry(zone_id, api_token, domain_name, public_ip)


if __name__ == "__main__":
    main()
