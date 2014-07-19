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

import os
import select
import socket

from rtp_packet import RTPPacket, ConnectionClosed, UnknownPayload

class DataEndpoints(object):
    def __init__(self, port):
        self.active = True
        self.sockets = {}
        self.poll = select.poll()

        trigger = os.pipe()
        self.trigger = os.fdopen(trigger[0], "r", 0), os.fdopen(trigger[1], "w", 0)
        self.sockets[trigger[0]] = self.trigger[0]
        self.poll.register(self.trigger[0], select.POLLIN)

        self.port_number = port + 1

    def handle(self):
        while self.active:
            sockets = self.poll.poll()

            if not self.active:
                return
            for (s, events) in sockets:
                if s == self.trigger[0].fileno():
                    self.trigger[0].read(1)
                else:
                    sobj = self.sockets[s]

                    if hasattr(sobj, "process"):
                        sobj.process()
                    else:
                        sobj.func(sobj, sobj.client)

    def stop(self):
        self.active = False
        for s in self.sockets.items():
            self.poll.unregister(s[0])
            s[1].close()
            del self.sockets[s[0]]
        self.trigger[1].close()

    def open_socket(self, func, client):
        while True:
            port = self.port_number
            self.port_number += 1

            try:
                s = TCPListener(port, self) if client.is_tcp else UDPSocket(port)
            except socket.error, e:
                if e[0] == 98: # Address already in use
                    continue
                else:
                    raise
            else:
                break

        s.func = getattr(self, func)
        s.client = client

        self.sockets[s.fileno()] = s
        self.poll.register(s, select.POLLIN)
        self.trigger[1].write("a")

        return port

    def server(self, s, client):
        try:
            client.audio_packet(RTPPacket(s))
        except ConnectionClosed:
            self.poll.unregister(s.fileno())
            del self.sockets[s.fileno()]
            s.close()
        except UnknownPayload, e:
            #print e
            pass

    def control(self, s, client):
        print "control", repr(s.recv(128))

    def timing(self, s, client):
        print "timing", repr(s.recv(128))

class UDPSocket(socket.socket):
    def __init__(self, port):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_DGRAM)
        self.bind(("", port))

class TCPListener(socket.socket):
    def __init__(self, port, de):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.bind(("", port))
        self.listen(1)
        self.de = de

    def process(self):
        s, addr = self.accept()
        s = TCPSocket(s, self.func, self.client)
        print "accepted", s.fileno()
        self.de.sockets[s.fileno()] = s
        self.de.poll.register(s, select.POLLIN)

class TCPSocket(object):
    def __init__(self, s, func, client):
        self.s = s
        self.func = func
        self.client = client

    def fileno(self):
        return self.s.fileno()

    def close(self):
        return self.s.close()

    def recv(self, buf):
        return self.s.recv(buf)
