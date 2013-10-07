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
import socket

class DataEndpoints(object):
    def __init__(self, port):
        self.active = True
        self.sockets = []
        self.port_number = port + 1

    def handle(self):
        while self.active:
            rsockets, _, _ = select.select(self.sockets, [], [])

            for s in rsockets:
                s.func(s, s.client)

    def stop(self):
        self.active = False
        for s in self.sockets:
            s.close()

    def open_socket(self, func, client):
        port = self.port_number
        self.port_number += 1

        s = UDPSocket(port)

        s.func = getattr(self, func)
        s.client = client

        self.sockets.append(s)

        return port

    def server(self, s, client):
        print "server", repr(s.read(128))

    def control(self, s, client):
        print "control", repr(s.read(128))

    def timing(self, s, client):
        print "timing", repr(s.read(128))

class UDPSocket(socket.socket):
    def __init__(self, port):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))
