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
import socket
import struct
from uuid import getnode as get_mac

import M2Crypto

rsa = M2Crypto.RSA.load_key("RAOP.key")

def apple_challenge(challenge, hwid):
    challenge = base64.b64decode(challenge)

    decoded = str(challenge) + ip_to_str() + hwid

    while len(decoded) < 32:
        decoded += "\0"

    value = base64.b64encode(rsa.private_encrypt(decoded, M2Crypto.RSA.pkcs1_padding))
    while value.endswith("="):
        value = value[:-1]

    return value

def ip_to_str():
    return socket.inet_aton("192.168.1.137")

if __name__ == "__main__":
    challenge = "Qdfy7ME9NejO/fUo/gZDsg=="
    myresp = apple_challenge(challenge, "\x00\x50\x29\x42\x60\x60")
    print "c0 a8 01 89"
    print "hwid: 005029426060"
    print
    print "Qdfy7ME9NejO/fUo/gZDssCoAYkAUClCYGAAAAAAAAA"
    print
    real = """GN5EwfoFUIza09qGOb04+SS+HPeMDYA8VF/z2LQVCEkd4IZbJDCUsO0b4cvVhsYrrZ42013UA/EhxMYO6jRynR4j7khORNs4blPAR/xWAuBv2uerl6sAbk7xqJRtBjRLHxfpw+/gn7z5hcnQT4gJJfBp77CBHSjkHuBhN2GyaSygH1qoeHyYJ2TE+hoUb8tNW/KQ7/uhH0LYNCRaj0Jm1Kw0qdm7DY0yFU5rxfbaO4b5BfI/z4CDfGvyo4bZo1Vm0Q25XyxTAl+6YBPjiVQW9l1z4LY8AULWAbIKQ4nM+Z+9F3oN3dKmIW8pMEYESnp+vCUGD+qz8tN5qlc6IyKSNQ"""
    print real
    print myresp
    print real == myresp
    d = base64.b64decode(real+"==")
    print base64.b64encode(rsa.public_decrypt(d, M2Crypto.RSA.pkcs1_padding))
