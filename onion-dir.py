#!/usr/bin/env python
#coding: utf-8

import struct
from socket import socket

from twisted.internet import defer, reactor
from twisted.names import server, dns
from twisted.names.common import ResolverBase

# Tunable values
PORT = 53
TOR_SERVER = ("127.0.0.1", 9050)
TIMEOUT = 3600
INTERFACE = "127.0.0.1"

# Protocol specific values
IPv4_Addr = 1
IPv6_Addr = 4
Tor_Succeed = 0 # Query succeeded

def unpack_ipv4_addr(raw_value):
    '''Converts a raw binary IPv4 address into it's dot-separated form.'''
    return '.'.join(map(lambda x: str(ord(x)), raw_value))

def unpack_ipv6_addr(raw_value):
    '''Converts a raw binary IPv6 address into it's colon-separated form.'''
    return ':'.join(map(lambda x: hex(ord(x)), raw_value))

def tor_lookup(sock, name):
    '''Looks up a name through a Tor socks5 server.'''
    name_len = struct.pack("B", len(name))

    sock.sendall("\x05\x01\x00") # Authtentication (lack of)
    authentication_check = sock.recv(2) # Should be 0x05 0x00 for SOCKS 5, no authentication

    # 0xF0 is Tor proxy RESOLVE command
    sock.sendall("\x05\xF0\x00\x03" + name_len + name + "\x00\x00")
    answer_confirmation = sock.recv(4)
    version, code, reserved, addr_type = struct.unpack("BBBB", answer_confirmation)

    if code != Tor_Succeed:
        return False

    if addr_type == IPv4_Addr:
        return unpack_ipv4_addr(sock.recv(4))

    elif addr_type == IPv6_Addr:
        return unpack_ipv6_addr(sock.recv(16))

class TorResolver(ResolverBase):
    def _lookup(self, name, cls, type, timeout=10):
        sock = socket()
        sock.connect(TOR_SERVER)
        result = tor_lookup(sock, name)
        sock.close()

        if not result:
            return defer.succeed([(), (), ()])

        return defer.succeed([
            (dns.RRHeader(name, dns.A, dns.IN, TIMEOUT, dns.Record_A(result, TIMEOUT)),), (), (),
            ])


resolver = TorResolver()
factory = server.DNSServerFactory(clients=[resolver])
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(PORT, protocol, interface=INTERFACE)
reactor.run()
