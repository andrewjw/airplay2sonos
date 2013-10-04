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
    "txtvers": "1",
    "ch": "2",
    "cn": "0,1",
    "ek": "1",
    "et": "0,1",
    "pw": "false",
    "sm": "false",
    "sv": "false",
    "sr": "44100",
    "ss": "16",
    "tp": "TCP",
    "vn": "3"
}

class BonjourRegistration(object):
    def __init__(self, name, regtype, port):
        self.registered = True

        self.name = name
        self.regtype = regtype
        self.port = port

    def callback(self, sdRef, flags, errorCode, name, regtype, domain):
        if errorCode == pybonjour.kDNSServiceErr_NoError:
            print "Bonjour registration complete! %s.%s" % (name, regtype)

    def register(self):
        self.record = pybonjour.TXTRecord(DEVICE_INFO)

        self.service = pybonjour.DNSServiceRegister(name = self.name,
                                            regtype = self.regtype,
                                            port = self.port,
                                            txtRecord = self.record,
                                            callBack = self.callback)

        while self.registered:
            ready = select.select([self.service], [], [])
            if self.registered and self.service in ready[0]:
                pybonjour.DNSServiceProcessResult(self.service)

    def stop(self):
        self.registered = False
        self.service.close()
