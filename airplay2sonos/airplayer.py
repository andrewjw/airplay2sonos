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
import threading

import bonjour
from protocol_handler import AirplayProtocolServer

class Application(object):
    def __init__(self, port):
        self._port = port

        self.hwid = "".join([chr(random.randint(0, 256)) for _ in range(6)])

    def run(self):
        self._register_bonjour()

        self._protocol_handler = AirplayProtocolServer(self._port, self.hwid)
        threading.Thread(target=self._protocol_handler.start).start()

    def _register_bonjour(self):
        hostname = "".join(["%02x" % ord(c) for c in self.hwid]) + "@Kitchen (Sonos)"

        threading.Thread(target=bonjour.register_service, args=(hostname, "_raop._tcp", self._port,)).start()
