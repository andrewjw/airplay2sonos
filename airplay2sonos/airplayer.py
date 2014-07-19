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

import random
import signal
import threading

import bonjour

from clients import Clients
from data_endpoints import DataEndpoints
from protocol_handler import AirplayProtocolServer

class Application(object):
    def __init__(self, port):
        self._port = port

        self.clients = Clients()
        self.endpoints = DataEndpoints(port)

        self.hwid = "".join([chr(random.randint(0, 255)) for _ in range(6)])

    def run(self):
        signal.signal(signal.SIGINT, self.handle_signal)

        self._register_bonjour()

        self.endpoint_thread = threading.Thread(target=self.endpoints.handle)
        self.endpoint_thread.daemon = True
        self.endpoint_thread.start()

        self._airplay_protocol_server = AirplayProtocolServer(self._port, self.hwid)
        self._airplay_protocol_server.start(self)

    def _register_bonjour(self):
        hostname = "".join(["%02x" % ord(c) for c in self.hwid]) + "@Kitchen (Sonos)"

        self.bonjour = bonjour.BonjourRegistration(hostname, "_raop._tcp", self._port)

        threading.Thread(target=self.bonjour.register).start()

    def handle_signal(self, signum, frame):
        self.bonjour.stop()
        self.endpoints.stop()
        threading.Thread(target=self._airplay_protocol_server.stop).start()
