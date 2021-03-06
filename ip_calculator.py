#!/bin/env python
from ip_address import ip_address_v4 as ip_address, ip_address_cidr
from sys import stdin
from common import list_add_and_str, unstring
import binutils

ip_class_table = [
        {"first":0x00000000, "netbits":7, "hostbits":24},
        {"first":0x80000000, "netbits":14, "hostbits":16},
        {"first":0xc0000000, "netbits":21, "hostbits":8},
        {"first":0xe0000000, "netbits":None, "hostbits":None},
        {"first":0xf0000000, "netbits":None, "hostbits":None},
        {"first":0x100000000, "netbits":None, "hostbits":None} #kinda stupid but makes a lot of things easier
]

def class2int(ip_class: chr):
    return 'ABCDE'.index(ip_class)

def int2class(i: int):
    return 'ABCDE'[i]

def get_ip_addr_class(ipaddr: ip_address):
    for i in range(5):
        if ipaddr < ip_class_table[i+1]["first"]:
            return int2class(i)

def ip_class_row(ipaddr: ip_address, offset=0):
    return ip_class_table[class2int(get_ip_addr_class(ipaddr)) + offset]

def get_ip_addr_network(ipaddr: ip_address):
    netbits = ip_class_row(ipaddr)["netbits"]
    return 2 ** netbits if netbits else "N/A"

def get_ip_addr_host(ipaddr: ip_address):
    hostbits = ip_class_row(ipaddr)["hostbits"]
    return 2 ** hostbits if hostbits else "N/A"

def get_ip_addr_first_address(ipaddr: ip_address):
    return ip_address(ip_class_row(ipaddr)["first"])

def get_ip_addr_last_address(ipaddr: ip_address):
    return ip_address(ip_class_row(ipaddr, offset=1)["first"] - 1)

def get_class_stats(ip_string: str):
    ipaddr=ip_address(ip_string)
    print(
"""Class: {}
Network: {}
Host: {}
First address: {}
Last address: {}""".format(
            get_ip_addr_class(ipaddr),
            get_ip_addr_network(ipaddr),
            get_ip_addr_host(ipaddr),
            get_ip_addr_first_address(ipaddr),
            get_ip_addr_last_address(ipaddr)
        )
    )

def ip_inverse(ip_address):
    return 0x100000000 - ip_address

def subnet_block_size(ipcidr: ip_address_cidr):
    return ip_inverse(int(ipcidr.mask))

def get_default_mask(ipaddr: ip_address):
    return ip_inverse(2 ** ip_class_row(ipaddr)["hostbits"])

def get_subnet_count(ipcidr: ip_address_cidr):
    return 2 ** binutils.leading_1s(int(ipcidr.mask - get_default_mask(ipcidr)))

def get_valid_subnet_ips(ipcidr: ip_address_cidr):
    subnet = ipcidr & ipcidr.mask
    max_address = subnet + subnet_block_size(ipcidr) * get_subnet_count(ipcidr)
    while subnet < max_address:
        yield subnet
        subnet += subnet_block_size(ipcidr)
    
def get_addressable_hosts_per_subnet(ipcidr: ip_address_cidr):
    return subnet_block_size(ipcidr) - 2

def get_valid_subnets(ipcidr: ip_address_cidr):
    return list_add_and_str( get_valid_subnet_ips(ipcidr) )

def get_broadcast_addresses(ipcidr: ip_address_cidr):
    return list_add_and_str( get_valid_subnet_ips(ipcidr), subnet_block_size(ipcidr) - 1 )

def get_first_addresses(ipcidr: ip_address_cidr):
    return list_add_and_str( get_valid_subnet_ips(ipcidr), 1 )

def get_last_addresses(ipcidr: ip_address_cidr):
    return list_add_and_str( get_valid_subnet_ips(ipcidr), subnet_block_size(ipcidr) - 2 )

def get_subnet_stats(ip_string: str, subnet_mask: str):
    ipcidr = ip_address_cidr(
            ip_string,
            ip_address(subnet_mask)
    )

    print(
"""Address: {}
Subnets: {}
Addressable hosts per subnet: {}
Valid subnets: {}
Broadcast addresses: {}
First addresses: {}
Last addresses: {}""".format(
            ipcidr,
            get_subnet_count(ipcidr),
            get_addressable_hosts_per_subnet(ipcidr),
            get_valid_subnets(ipcidr),
            get_broadcast_addresses(ipcidr),
            get_first_addresses(ipcidr),
            get_last_addresses(ipcidr)
        )
    )

def get_supernet_address(ipaddrs):
    mask = get_supernet_mask(ipaddrs)
    return ip_address_cidr(
            int(ipaddrs[0] & mask),
            mask
        )

def get_supernet_mask(ipaddrs):
    common_bits = binutils.xnor_all(*ipaddrs)
    leading_1s = binutils.leading_1s(common_bits)
    return ip_address( binutils.n1s_then_n0s( leading_1s, 32 - leading_1s))

def get_supernet_stats(ip_strings: list):
    ips = [ip_address(s) for s in ip_strings]
    print(
"""Address: {} 
Network Mask: {}""".format(
            get_supernet_address(ips),
            get_supernet_mask(ips)
        )
    )

def main():
    for line in stdin:
        print(line.strip())
        try:
            a = unstring(line)
            assert(type(a) is list)
            get_supernet_stats(a)
        except AssertionError:
            addr_strings = line.strip().split(',')
            get_class_stats(addr_strings[0])
            try:
                get_subnet_stats(addr_strings[0], addr_strings[1])
            except IndexError:
                pass
        print()

if __name__ == "__main__":
    main()
