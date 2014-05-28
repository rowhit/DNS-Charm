import os
import sys
from .zoneparser import ZoneParser

# Add charmhelpers to the system path.
try:
    sys.path.insert(0, os.path.abspath(os.path.join(os.environ['CHARM_DIR'],
                                                    'lib')))
except:
    sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'lib')))

from charmhelpers.core.hookenv import open_port, log, unit_get

from charmhelpers.fetch import (
    apt_install,
    apt_update,
)


class BindProvider(object):

    def install(self):
        apt_update(fatal=True)
        apt_install(packages=[
            'bind9',
            'dnsutils',
            ], fatal=True)
        open_port(53)

    def config_changed(self, domain='example.com'):
        zp = ZoneParser(domain)
        # Install a skeleton bind zone, rehashes existing file
        # if it has contents)
        self.first_setup(zp, domain)
        zp.save()

    def add_record(self, domain='example.com', record={}):
        if not record:
            log('No record dictionary found, returning')
        zp = ZoneParser(domain)
        zp.dict_to_zone(record)
        zp.save()

    def first_setup(self, parser, domain='example.com'):
        # Insert SOA and NS records
        addr = unit_get('public-address')
        parser.dict_to_zone({'rr': 'SOA',
                             'addr': '@',
                             'alias': 'root.%s' % domain,
                             'serial': '2003080800',
                             'refresh': '12h',
                             'update-retry': '15m',
                             'expiry': '3w',
                             'minimum': '3h'})
        parser.dict_to_zone({'rr': 'NS', 'owner-name': '@',
                             'addr': 'ns1.%s.' % domain})
        parser.dict_to_zone({'rr': 'A', 'alias': '@', 'addr': addr})
        parser.dict_to_zone({'rr': 'A', 'alias': 'ns1', 'addr': addr})