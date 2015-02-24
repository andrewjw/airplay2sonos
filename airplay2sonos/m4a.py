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

import struct
import time

class QTFFAtomMeta(type):
    def __new__(cls, name, bases, attrs):
        newattrs = {}

        for attr in attrs:
            if 

        return super(QTFFAtomMeta, cls).__new__(cls, name, bases, newattrs)

class M4AAtom(object):
    def __init__(self, atom, data):
        self.atom = atom
        self.data = data

    def __str__(self):
        return struct.pack(">icccc", 8+len(self.data), self.atom[0], self.atom[1], self.atom[2], self.atom[3]) + self.data

class M4AFile(object):
    def __init__(self, fp, fmtp):
        self.fp = fp
        self.fmtp = [int(x) for x in fmtp.split(" ")]
        self.bits = 0
        self.byte = 0

    def write_header(self):
        self.fp.write(str(M4AAtom("ftyp", "M4A " + struct.pack(">i", 0x200))))
        self.fp.write(str(M4AAtom("free", "")))

        mvhd = M4AAtom("mvhd", struct.pack(">BBBBiiii", 0, 0, 0, 0, int(time.time()), int(time.time()), 1, 60*60, ))

        self.fp.write(str(M4AAtom("moov", "".join([str(MVHD(self.fmtp[-1])), str(Trak(self.fmtp))]))))

        self.fp.write(struct.pack(">icccc", 0, "m", "d", "a", "t"))

    def write(self, data):
        for byte in data:
            self.write_bits(ord(byte), 8)

    def write_bits(self, data, bits):
        if bits > 8:
            self.write_bits(data >> (bits - 8), 8)
            self.write_bits(data & ((2 ** (bits - 8)) - 1), bits - 8)
        elif self.bits == 0 and bits == 8: # No mangling required
            self.fp.write(chr(data))
        elif bits + self.bits < 8:
            self.byte = self.byte << bits | data
            self.bits += bits
        else:
            self.fp.write(chr(self.byte << (8 - self.bits) | data >> bits - (8 - self.bits)))
            self.bits = bits - (8 - self.bits)
            self.byte = data & ((2 ** self.bits) - 1)

    def flush(self):
        self.fp.flush()

class MVHD(object):
    def __init__(self, sample_rate):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.ctime = struct.pack(">i", int(time.time()))
        self.mtime = struct.pack(">i", int(time.time()))
        self.time_scale = struct.pack(">i", sample_rate)
        self.duration = struct.pack(">i", 60) # We're streaming so we don't know the duration
        self.preferred_rate = struct.pack(">HH", 1, 0)
        self.preferred_volume = struct.pack(">HH", 1, 0)
        self.reserved = struct.pack("10B", *(10*[0]))
        self.matrix = struct.pack("36B", *(36*[0]))
        self.preview_time = struct.pack(">i", 0)
        self.preview_duration = struct.pack(">i", 0)
        self.poster_time = struct.pack(">i", 0)
        self.selection_time = struct.pack(">i", 0)
        self.selection_duration = struct.pack(">i", 0)
        self.current_time = struct.pack(">i", 0)
        self.next_track = struct.pack(">i", 1)

    def __str__(self):
        return str(M4AAtom("mvhd", "".join([self.version,
                                        self.flags,
                                        self.ctime,
                                        self.mtime,
                                        self.time_scale,
                                        self.duration,
                                        self.preferred_rate,
                                        self.preferred_volume,
                                        self.reserved,
                                        self.matrix,
                                        self.preview_time,
                                        self.preview_duration,
                                        self.poster_time,
                                        self.selection_time,
                                        self.selection_duration,
                                        self.current_time,
                                        self.next_track])))

class Trak(object):
    def __init__(self, fmtp):
        self.fmtp = fmtp

    def __str__(self):
        return str(M4AAtom("trak", "".join([str(TKHD()), str(MDIA(self.fmtp))])))

class TKHD(object):
    def __init__(self):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 255)
        self.ctime = struct.pack(">i", int(time.time()))
        self.mtime = struct.pack(">i", int(time.time()))
        self.track_id = struct.pack(">i", 1)
        self.reserved1 = struct.pack(">i", 0)
        self.duration = struct.pack(">i", 0) # We're streaming so we don't know the duration
        self.reserved2 = struct.pack(">ii", 0, 0)
        self.layer = struct.pack(">H", 1)
        self.alternate_group = struct.pack(">H", 0)
        self.volume = struct.pack("BB", 1, 0)
        self.reserved3 = struct.pack("H", 0)
        self.matrix = struct.pack("36B", *(36*[0]))
        self.track_size = struct.pack(">ii", 0, 0)

    def __str__(self):
        return str(M4AAtom("tkhd", "".join([self.version,
                                            self.flags,
                                            self.ctime,
                                            self.mtime,
                                            self.track_id,
                                            self.reserved1,
                                            self.duration,
                                            self.reserved2,
                                            self.layer,
                                            self.alternate_group,
                                            self.volume,
                                            self.reserved3,
                                            self.matrix,
                                            self.track_size])))

class MDIA(object):
    def __init__(self, fmtp):
        self.fmtp = fmtp

    def __str__(self):
        return str(M4AAtom("mdia", "".join([str(MDHD(self.fmtp[-1])), str(MINF(self.fmtp))])))

class MDHD(object):
    def __init__(self, sample_rate):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.ctime = struct.pack(">i", int(time.time()))
        self.mtime = struct.pack(">i", int(time.time()))
        self.time_scale = struct.pack(">i", sample_rate)
        self.duration = struct.pack(">i", 0)
        self.language = struct.pack(">H", 32767)
        self.quality = struct.pack(">H", 0)

    def __str__(self):
        return str(M4AAtom("mdhd", "".join([self.version,
                                            self.flags,
                                            self.ctime,
                                            self.mtime,
                                            self.time_scale,
                                            self.duration,
                                            self.language,
                                            self.quality])))

class MINF(object):
    def __init__(self, fmtp):
        self.fmtp = fmtp

    def __str__(self):
        return str(M4AAtom("minf", "".join([str(SMHD()), str(DINF()), str(STBL(self.fmtp))])))

class HDLR(object):
    def __init__(self, sample_rate):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.component = "mhlr"
        self.component_subtype = "soun"
        self.manufacturer = struct.pack(">i", 0)
        self.flags = struct.pack(">i", 0)
        self.flags_mask = struct.pack(">i", 0)
        self.component_name = ""

    def __str__(self):
        return str(M4AAtom("hdlr", "".join([self.version,
                                            self.flags,
                                            self.component,
                                            self.component_subtype,
                                            self.manufacturer,
                                            self.flags,
                                            self.flags_mask,
                                            self.component_name])))


class SMHD(object):
    def __init__(self):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.balance = struct.pack("BB", 0, 0)
        self.reserved = struct.pack("BB", 0, 0)

    def __str__(self):
        return str(M4AAtom("smhd", "".join([self.version, self.flags, self.balance, self.reserved])))

class STBL(object):
    def __init__(self, fmtp):
        self.fmtp = fmtp

    def __str__(self):
        return str(M4AAtom("stbl", "".join([str(STSD(self.fmtp))])))

class DINF(object):
    def __init__(self):
        pass

    def __str__(self):
        return str(M4AAtom("dinf", "".join([str(DREF())])))

class DREF(object):
    def __init__(self):
        self.version = struct.pack("B", 0)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.count = struct.pack(">I", 0)

    def __str__(self):
        return str(M4AAtom("dref", "".join([self.version, self.flags, self.count])))

class STSD(object):
    def __init__(self, fmtp):
        self.fmtp = fmtp
        self.version = struct.pack("B", 1)
        self.flags = struct.pack("BBB", 0, 0, 0)
        self.count = struct.pack(">I", 1)

    def __str__(self):
        return str(M4AAtom("stsd", "".join([self.version, self.flags, self.count, str(ALAC(self.fmtp))])))

class ALAC(object):
    def __init__(self, fmtp):
        assert fmtp[0] == 96, "Format not Apple Lossless"

        self.blank = struct.pack("BBBBBB", 0, 0, 0, 0, 0, 0)
        self.version = struct.pack(">H", 0)
        self.revision = struct.pack(">H", 0)
        self.vendor = struct.pack(">I", 1)
        self.mystery = struct.pack(">H", 0) # Not mentioned in spec, but in the files...
        self.channels = struct.pack(">H", fmtp[7])
        self.bit_depth = struct.pack(">H", fmtp[3])
        self.compression = struct.pack(">H", 0)
        self.packet = struct.pack(">H", 0)
        self.sample_rate = struct.pack(">HH", fmtp[11], 0)
        #self.samples_per_packet = struct.pack(">i", fmtp[1])
        #self.bytes_per_packet = struct.pack(">i", fmtp[1] * 2)
        #self.bytes_per_frame = struct.pack(">i", fmtp[9])
        #self.bytes_per_sample = struct.pack(">i", 2)
        #self.version = struct.pack("B", 1)
        #self.pb = struct.pack("B", fmtp[4])
        #self.mb = struct.pack("B", fmtp[5])
        #self.kb = struct.pack("B", fmtp[6])
        #self.max_run = struct.pack(">H", fmtp[8])
        #self.avg_bit_rate = struct.pack(">i", fmtp[10])

    def __str__(self):
        return str(M4AAtom("alac", "".join([self.blank,
                                            self.version,
                                            self.revision,
                                            self.vendor,
                                            self.channels,
                                            self.bit_depth,
                                            self.compression,
                                            self.packet,
                                            self.sample_rate,
                                            self.samples_per_packet,
                                            self.bytes_per_packet,
                                            self.bytes_per_frame,
                                            self.bytes_per_sample])))
