import fcntl
import struct
import os
import ctypes

from labdevices.i2cbus import I2CBus

class IICCmd(ctypes.Structure):
    _fields_ = [
        ( "slave", ctypes.c_ubyte ),
        ( "count", ctypes.c_int ),
        ( "last", ctypes.c_int ),
        ( "buf", ctypes.c_void_p )
    ]

class IICMsg(ctypes.Structure):
    _fields_ = [
        ( "slave", ctypes.c_uint16 ),
        ( "flags", ctypes.c_uint16 ),
        ( "len", ctypes.c_uint16 ),
        ( "buf", ctypes.c_void_p )
    ]

class IICMsg2(ctypes.Structure):
    _fields_ = [
        ( "m1", IICMsg ),
        ( "m2", IICMsg )
    ]

class IICRdwrData(ctypes.Structure):
    _fields_ = [
        ( "msgs", ctypes.POINTER(IICMsg) ),
        ( "nmsgs", ctypes.c_uint32 )
    ]

class FbsdI2C(I2CBus):
    def __init__(
        self,
        devname = "/dev/iic0"
    ):
        self._devname = devname
        self._handle = None

        # IOCTL numbers
        self._I2CRDWR = 2148559110

        self._handle = os.open(self._devname, os.O_RDWR)

    def __del__(self):
        if self._handle is not None:
            try:
                os.close(self._handle)
                self._handle = None
            except:
                pass

    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return


    def scan(
        self
    ):
        msgs = IICMsg2()
        rdwr = IICRdwrData()
        buf = ctypes.create_string_buffer(bytes(bytearray([0,0])), 2)

        msgs.m1.flags = 0
        msgs.m1.len = 2
        msgs.m1.buf = ctypes.cast(buf, ctypes.c_void_p)
        msgs.m2.flags = 1
        msgs.m2.len = 2
        msgs.m2.buf = ctypes.cast(buf, ctypes.c_void_p)

        foundDevs = []
        for i2cAddress in range(1, 128):
            msgs.m1.slave = i2cAddress << 1
            msgs.m2.slave = i2cAddress << 1
            rdwr.nmsgs = 2
            rdwr.msgs = ctypes.cast(ctypes.pointer(msgs), ctypes.POINTER(IICMsg))
            foundDevice = False
            try:
                fcntl.ioctl(self._handle, self._I2CRDWR, rdwr)
                foundDevs.append(i2cAddress)
                foundDevice = True
            except IOError as e:
                pass

        return foundDevs

    def read(
        self,
        device,
        nbytes = 1,
        raiseException = False
    ):
        msg = IICMsg()
        rdwr = IICRdwrData()
        inbuffer = ctypes.c_char * int(nbytes)

        indatabuffer = []
        for _ in range(nbytes):
            indatabuffer.append(0)
        indatabuffer = bytearray(indatabuffer)

        msg.slave = device << 1
        msg.flags = 1
        msg.len = nbytes
        msg.buf = ctypes.cast(inbuffer.from_buffer(indatabuffer), ctypes.c_void_p)
        rdwr.msgs = ctypes.pointer(msg)
        rdwr.nmsgs = 1

        try:
            fcntl.ioctl(self._handle, self._I2CRDWR, rdwr)
        except Exception as e:
            if raiseException:
                raise e
            else:
                return None

        return indatabuffer

    def write(
        self,
        device,
        data,
        raiseException = False
    ):
        data = bytearray(data)
        rdwr = IICRdwrData()
        outbuffer = ctypes.c_char * int(len(data))
        msg = IICMsg()

        msg.slave = device << 1
        msg.flags = 0
        msg.len = int(len(data))
        msg.buf = ctypes.cast(outbuffer.from_buffer(data), ctypes.c_void_p)
        rdwr.msgs = ctypes.pointer(msg)
        rdwr.nmsgs = 1

        try:
            fcntl.ioctl(self._handle, self._I2CRDWR, rdwr)
        except Exception as e:
            if raiseException:
                raise e
            return False

        return True

    def writeread(
        self,
        device,
        dataOut,
        lenIn,
        raiseException = False
    ):
        dataOut = bytearray(dataOut)
        rdwr = IICRdwrData()
        outbuffer = ctypes.c_char * int(len(dataOut))
        inbuffer = ctypes.c_char * int(lenIn)
        indatabuffer = []
        for _ in range(lenIn):
            indatabuffer.append(0)
        indatabuffer = bytearray(indatabuffer)

        rdwr = IICRdwrData()
        msg = IICMsg2()

        msg.m1.slave = device << 1
        msg.m1.flags = 0
        msg.m1.len = int(len(dataOut))
        msg.m1.buf = ctypes.cast(outbuffer.from_buffer(dataOut), ctypes.c_void_p)

        msg.m2.slave = device << 1
        msg.m2.flags = 1
        msg.m2.len = lenIn
        msg.m2.buf = ctypes.cast(inbuffer.from_buffer(indatabuffer), ctypes.c_void_p)

        rdwr.msgs = ctypes.cast(ctypes.pointer(msg), ctypes.POINTER(IICMsg))
        rdwr.nmsgs = 2

        try:
            fcntl.ioctl(self._handle, self._I2CRDWR, rdwr)
        except Exception as e:
            if raiseException:
                raise e
            return None

        return indatabuffer

    def __repr__(self):
        return f"FbsdI2C(devname=\"{self._devname}\")"
