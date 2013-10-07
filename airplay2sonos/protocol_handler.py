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

import base64
import BaseHTTPServer
import SocketServer
import threading

from apple_challenge import apple_challenge

class AirplayProtocolServer(object):
    def __init__(self, port, hwid):
        self._http_server = None
        self._port = port
        self._hwid = hwid

    def start(self, airplayer):
        self._httpd = ThreadedHTTPServer(("", self._port), AirplayProtocolHandler)
        self._httpd.airplayer = airplayer
        self._httpd.hwid = self._hwid
        self._httpd.serve_forever()

    def stop(self):
        self._httpd.shutdown()

class ThreadedHTTPServer(BaseHTTPServer.HTTPServer):
    daemon_threads = True

class AirplayProtocolHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def parse_request(self):
        self.raw_requestline = self.raw_requestline.replace("RTSP/1.0", "HTTP/1.1")

        r = BaseHTTPServer.BaseHTTPRequestHandler.parse_request(self)
        self.protocol_version = "RTSP/1.0"
        self.close_connection = 0
        return r

    def do_OPTIONS(self):
        self.send_response(200)

        if "Apple-Challenge" in self.headers:
            self.send_header("Apple-Response", apple_challenge(self.headers["Apple-Challenge"], self.server.hwid))

        self.send_header("Audio-Jack-Status", "connected; type=analog")
        self.send_header("Public", "ANNOUNCE, SETUP, RECORD, PAUSE, FLUSH, TEARDOWN, OPTIONS, GET_PARAMETER, SET_PARAMETER")

        self.end_headers()

    def do_GET(self):
        print self.headers
        print self.rfile.read()

    def do_POST(self):
        print self.headers
        print self.rfile.read()

    def do_ANNOUNCE(self):
        raw_attrs = self.rfile.read(int(self.headers["Content-Length"]))

        attrs = {}
        for line in raw_attrs.split("\n"):
            if "=" not in line:
                continue

            key = line.split("=")[0]
            value = "=".join(line.split("=")[1:]).strip()

            if key == "a":
                attrs[value.split(":")[0]] = ":".join(value.split(":")[1:])
            else:
                attrs[key] = value

        self._id = self.server.airplayer.clients.new_client(attrs)

        self.send_response(200)
        self.end_headers()

    def do_SETUP(self):
        print self.headers
        print self.rfile.read()

    def do_RECORD(self):
        print self.headers
        print self.rfile.read()
        
    def send_response(self, code, message=None):
        """Send the response header and log the response code.

        Also send two standard headers with the server software
        version and the current date.

        """
        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            self.wfile.write("%s %d %s\r\n" %
                             (self.protocol_version, code, message))
        if "CSeq" in self.headers:
            self.send_header("CSeq", self.headers["CSeq"])

    # From: http://blog.gocept.com/2011/08/04/shutting-down-an-httpserver/
    _continue = True

    def serve_forevere(self):
        while self._continue:
            self.handle_request()

    def shutdown(self):
        self._running = False
        # We fire a last request at the server in order to take it out of the
        # while loop in `self.serve_until_shutdown`.
        try:
            urllib2.urlopen(
                'http://%s:%s/' % (self.server_name, self.server_port))
        except urllib2.URLError:
            # If the server is already shut down, we receive a socket error,
            # which we ignore.
            pass
        self.server_close()
