__author__ = "SutandoTsukai181"
__copyright__ = "Copyright 2021, SutandoTsukai181"
__license__ = "MIT"
__version__ = "1.1"

import struct
from typing import Tuple, Union

FMT = dict()
for c in ["b", "B", "s"]:
    FMT[c] = 1
for c in ["h", "H", "e"]:
    FMT[c] = 2
for c in ["i", "I", "f"]:
    FMT[c] = 4
for c in ["q", "Q"]:
    FMT[c] = 8


class BinaryReader:
    """A buffer reader/writer containing a mutable bytearray.\n
    Allows reading and writing various data types, while advancing the position of the buffer on each operation."""
    __buf: bytearray
    __idx: int
    __big_end: bool

    def __init__(self, buffer=bytearray(), big_endian=False):
        """Constructs a BinaryReader with the given buffer and endianness and sets its position to 0.\n
        If buffer is not given, a new bytearray() is created. If endianness is not given, it is set to little endian.
        """
        self.__buf = bytearray(buffer)
        self.__big_end = big_endian
        self.__idx = 0

    def pos(self) -> int:
        """Returns the current position in the buffer."""
        return self.__idx

    def size(self) -> int:
        """Returns the size of the buffer."""
        return len(self.__buf)

    def buffer(self) -> bytearray:
        """Returns the buffer as a bytearray."""
        return bytearray(self.__buf)

    def pad(self, size: int) -> None:
        """Extends the buffer by 0s with the given size."""
        self.__buf.extend([0] * size)

    def align(self, size: int) -> None:
        """Aligns the buffer to the given size.\n
        Extends the buffer starting from the current position by (size - (position % size)).
        """
        if self.__idx % size:
            pad = size - (self.__idx % size)
            self.pad(pad)
            return pad
        return 0

    def extend(self, buffer: bytearray) -> None:
        """Extends the BinaryReader's buffer with the given buffer."""
        self.__buf.extend(buffer)

    def seek(self, offset: int, whence=0) -> None:
        """Changes the current position of the buffer by the given offset.\n
        The seek is determined relative to the whence:\n
        whence = 0 will seek relative to the start.\n
        whence = 1 will seek relative to the current position.\n
        whence = 2 will seek relative to the end (offset should be positive).
        """
        if whence == 0:
            if offset > len(self.__buf):
                raise Exception(
                    'BinaryReader Error: cannot seek farther than buffer length.')
            else:
                self.__idx = offset
        elif whence == 1:
            if self.__idx + offset > len(self.__buf):
                raise Exception(
                    'BinaryReader Error: cannot seek farther than buffer length.')
            else:
                self.__idx += offset
        elif whence == 2:
            if offset >= len(self.__buf):
                raise Exception(
                    'BinaryReader Error: cannot seek farther than buffer length.')
            else:
                self.__idx = (len(self.__buf) - 1) - offset

    def set_endian(self, is_big_endian: bool) -> None:
        """Sets the endianness of the BinaryReader."""
        self.__big_end = is_big_endian

    def __read_type(self, format: str, count=1):
        i = self.__idx
        self.__idx += FMT[format] * count

        end = ">" if self.__big_end else "<"

        return struct.unpack_from(end + str(count) + format, self.__buf, i)

    def read_bytes(self, length=1) -> bytes:
        """Reads a bytes object with the given length from the current position."""
        return self.__read_type("s", length)

    def read_str(self, length=0, encoding='utf-8') -> str:
        """Reads a string with the given length from the current position.\n
        If length is 0, will read until the first null byte (which the position will be set after).\n
        Default encoding is UTF-8.
        """
        if length == 0:
            string = bytearray()
            while self.__idx < len(self.__buf):
                string.append(self.__buf[self.__idx])
                self.__idx += 1
                if string[-1] == 0:
                    break

            return string.split(b'\x00', 1)[0].decode(encoding)

        return self.read_bytes(length)[0].split(b'\x00', 1)[0].decode(encoding)

    def read_int64(self, count=1) -> Union[int, Tuple[int]]:
        """Reads a signed 64-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("q", count)
        return self.__read_type("q")[0]

    def read_uint64(self, count=1) -> Union[int, Tuple[int]]:
        """Reads an unsigned 64-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("Q", count)
        return self.__read_type("Q")[0]

    def read_int32(self, count=1) -> Union[int, Tuple[int]]:
        """Reads a signed 32-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("i", count)
        return self.__read_type("i")[0]

    def read_uint32(self, count=1) -> Union[int, Tuple[int]]:
        """Reads an unsigned 32-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("I", count)
        return self.__read_type("I")[0]

    def read_int16(self, count=1) -> Union[int, Tuple[int]]:
        """Reads a signed 16-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("h", count)
        return self.__read_type("h")[0]

    def read_uint16(self, count=1) -> Union[int, Tuple[int]]:
        """Reads an unsigned 16-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("H", count)
        return self.__read_type("H")[0]

    def read_int8(self, count=1) -> Union[int, Tuple[int]]:
        """Reads a signed 8-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("b", count)
        return self.__read_type("b")[0]

    def read_uint8(self, count=1) -> Union[int, Tuple[int]]:
        """Reads an unsigned 8-bit integer.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("B", count)
        return self.__read_type("B")[0]

    def read_float(self, count=1) -> Union[float, Tuple[float]]:
        """Reads a 32-bit float.\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("f", count)
        return self.__read_type("f")[0]

    def read_half_float(self, count=1) -> Union[float, Tuple[float]]:
        """Reads a 16-bit float (half-float).\n
        If count is greater than 1, will return a tuple of values instead of 1 value.
        """
        if count > 1:
            return self.__read_type("e", count)
        return self.__read_type("e")[0]

    def __write_type(self, format: str, value, is_iterable: bool) -> None:
        i = self.__idx

        end = ">" if self.__big_end else "<"

        count = 1
        if is_iterable or type(value) is bytes:
            count = len(value)

        if i + (FMT[format] * count) > len(self.__buf):
            self.pad(FMT[format] * count)

        if is_iterable:
            struct.pack_into(end + str(count) + format, self.__buf, i, *value)
        else:
            struct.pack_into(end + str(count) + format, self.__buf, i, value)

        self.__idx += FMT[format] * count

    def write_bytes(self, value: bytes) -> None:
        """Writes a bytes object to the buffer."""
        self.__write_type("s", value, is_iterable=False)

    def write_str(self, string: str, null=False, encoding='utf-8') -> None:
        """Writes a whole string to the buffer.\n
        If null is True, will append a null byte (0x00) after the string.\n
        Default encoding is UTF-8.
        """
        self.write_bytes(string.encode(encoding) + (b'\x00' if null else b''))

    def write_int32(self, value: int, is_iterable=False) -> None:
        """Writes a signed 32-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("i", value, is_iterable)

    def write_uint32(self, value: int, is_iterable=False) -> None:
        """Writes an unsigned 32-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("I", value, is_iterable)

    def write_int16(self, value: int, is_iterable=False) -> None:
        """Writes a signed 16-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("h", value, is_iterable)

    def write_uint16(self, value: int, is_iterable=False) -> None:
        """Writes an unsigned 16-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("H", value, is_iterable)

    def write_int8(self, value: int, is_iterable=False) -> None:
        """Writes a signed 8-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("b", value, is_iterable)

    def write_uint8(self, value: int, is_iterable=False) -> None:
        """Writes an unsigned 8-bit integer.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("B", value, is_iterable)

    def write_float(self, value: float, is_iterable=False) -> None:
        """Writes a 32-bit float.\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("f", value, is_iterable)

    def write_half_float(self, value: float, is_iterable=False) -> None:
        """Writes a 16-bit float (half-float).\n
        If is_iterable is True, will write all of the values in the given iterable.
        """
        self.__write_type("e", value, is_iterable)
