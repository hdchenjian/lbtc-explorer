#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Resolves hostname and GeoIP data for each reachable node. """

import geoip2.database
from geoip2.errors import AddressNotFoundError
from decimal import Decimal
#import reverse_geocoder

# MaxMind databases
GEOIP_CITY = geoip2.database.Reader("geoip/GeoLite2-City.mmdb")
GEOIP_COUNTRY = geoip2.database.Reader("geoip/GeoLite2-Country.mmdb")
ASN = geoip2.database.Reader("geoip/GeoLite2-ASN.mmdb")


def resolve_address(address):
    try:
        gcity = GEOIP_CITY.city(address)
        prec = Decimal('.000001')
        if gcity.location.latitude is not None and gcity.location.longitude is not None:
            lat = float(Decimal(gcity.location.latitude).quantize(prec))
            lng = float(Decimal(gcity.location.longitude).quantize(prec))
        timezone = gcity.location.time_zone
        
        gcountry = GEOIP_COUNTRY.country(address)
    
        if address.endswith(".onion"):
            asn = "TOR"
            org = "Tor network"
        else:
            asn_record = ASN.asn(address)
            asn = 'AS{}'.format(asn_record.autonomous_system_number)
            org = asn_record.autonomous_system_organization
        #print dir(gcity), gcity.raw
        city_name = gcity.city.name
        print(gcity.city.name, gcountry.country.iso_code, lat, lng, timezone, asn, org)
        if city_name is None:
            city_name = gcity.country.names['en']
        else:
            city_name = city_name + ', ' + gcity.country.names['en'] + '' + timezone
        print city_name
        print org + '|' + asn
        
    except AddressNotFoundError:
        pass
    

if __name__ == '__main__':
    address = '93.4.85.111'
    address = '120.79.161.218'
    resolve_address(address)
