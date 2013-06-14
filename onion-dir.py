#!/usr/bin/env python
#coding: utf-8

import os
import sys
import struct

from socket import socket

from twisted.internet import defer, reactor
from twisted.names import server, dns
from twisted.names.common import ResolverBase

# Tunable values
DAEMONIZE = True
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

        if '.' in result:  # Dot-separated IPv4 address
            return defer.succeed([
                (dns.RRHeader(name, dns.A, dns.IN, TIMEOUT,
                              dns.Record_A(result, TIMEOUT)),), (), (),
            ])

        else:  # Guess colon-separated IPv6 address
            return defer.succeed([
                (dns.RRHeader(name, dns.AAAA, dns.IN, TIMEOUT,
                              dns.Record_AAAA(result, TIMEOUT)),), (), (),
            ])




def daemonize():
    '''Detach process.'''
    pid = os.fork()
    if pid == 0: # Forked process
        os.chdir('/') # Unlock directory
        os.umask(0)

    else: # Parent process
        exit(0)

    # Detach file descriptors
    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

def show_help(arg0='onion-dir.py'):
    '''Show CLI options.'''
    print "Syntax: {arg0} (-f|-d) [-h]\n".format(arg0=arg0)
    print "-f: Launch in foreground"
    print "-d: Launch in the background (default)"
    print "-h: Show this help and exit"


if __name__ == "__main__":
    for param in sys.argv[1:]:
        if param == '-d':
            DAEMONIZE = True
        elif param == '-f':
            DAEMONIZE = False
        elif param == '-h':
            show_help(sys.argv[0])
            exit(0)

    if DAEMONIZE:
        daemonize()

    resolver = TorResolver()
    factory = server.DNSServerFactory(clients=[resolver])
    protocol = dns.DNSDatagramProtocol(factory)

    reactor.listenUDP(PORT, protocol, interface=INTERFACE)
    reactor.run()
