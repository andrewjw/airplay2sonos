#    airplay2sonos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import select
import pybonjour
import logging

DEVICE_INFO = {
    'deviceid' : 'FF:FF:FF:FF:FF:FF',
    'features' : '0x77',
    'model' : 'AppleTV2,1',
    'srcvers' : '101.10'
}

def register_service(name, regtype, port):
    def register_callback(sdRef, flags, errorCode, name, regtype, domain):
        print sdRef, flags, errorCode, name, regtype, domain
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print "Bonjour registration complete! %s.%s" % (name, regtype)

    record = pybonjour.TXTRecord(DEVICE_INFO)

    service = pybonjour.DNSServiceRegister(name = name,
                                         regtype = regtype,
                                         port = port,
                                         txtRecord = record,
                                         callBack = register_callback)

    try:
        while True:
            ready = select.select([service], [], [])
            if service in ready[0]:
                pybonjour.DNSServiceProcessResult(service)
    except KeyboardInterrupt:
        pass
    finally:
        service.close()
