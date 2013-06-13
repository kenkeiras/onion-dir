#!/usr/bin/env python
#coding: utf-8

import subprocess

from twisted.internet import defer, reactor
from twisted.names import server, dns
from twisted.names.common import ResolverBase

class TorResolver(ResolverBase):
    def _lookup(self, name, cls, type, timeout=10):
        proc = subprocess.Popen(["tor-resolve", name],
                                stdout=subprocess.PIPE)

        response = proc.stdout.read().strip()
        return defer.succeed([
            (dns.RRHeader(name, dns.A, dns.IN, 3600, dns.Record_A(response, 3600)),), (), (),
            ])


resolver = TorResolver()
factory = server.DNSServerFactory(clients=[resolver])
protocol = dns.DNSDatagramProtocol(factory)

reactor.listenUDP(53, protocol)
reactor.run()
