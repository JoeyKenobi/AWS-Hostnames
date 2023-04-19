import json
import logging
import netaddr
import os
import requests
import sys


class AWSIPs:
    def __init__(self, sync_token, create_date, prefixes):
        self.sync_token = sync_token
        self.create_date = create_date
        self.prefixes = prefixes


def main():
    try:
        response = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json', timeout=10)
        response.raise_for_status()
        data = json.loads(response.content)
        aws_ips = AWSIPs(data['syncToken'], data['createDate'], data['prefixes'])
    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error('Error fetching or decoding AWS IP ranges: %s', str(e))
        sys.exit(1)

    for prefix in aws_ips.prefixes:
        prefix_dict = dict(prefix)
        cidr = prefix_dict.get('ip_prefix', '')
        try:
            ips = netaddr.IPNetwork(cidr).iter_hosts()
        except netaddr.core.AddrFormatError as e:
            logging.error('Error expanding CIDR: %s', str(e))
            continue

        for ip in ips:
            ip_str = str(ip).replace('.', '-')
            domain_name = f'ec2-{ip_str}.{prefix_dict["region"]}.compute.amazonaws.com'
            print(domain_name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    main()