import struct
import typing as _typ

import pygame


class ByteBuffer:
    """Wrapper around a bytes or bytearray object.
    Provides methods to read and write Python to the underlying object.
    """

    def __init__(self, source: bytes | bytearray = None):
        """Create a byte buffer wrapping the given object.
        If no source is provided, the buffer is initialized with a new empty bytearray.

        :param source: Bytes to wrap.
        """
        self._read_index = 0
        self._bytes: bytes | bytearray = source if source is not None else bytearray()

    @property
    def bytes(self) -> bytes | bytearray:
        """The underlying object wrapped by this buffer."""
        return self._bytes

    def __len__(self):
        """Return the number of bytes in this buffer."""
        return len(self._bytes)

    def __iter__(self) -> _typ.Iterator[int]:
        """Return an iterator over the internal bytearray object."""
        return iter(self._bytes)

    def read_bool(self) -> bool:
        """Read a boolean value then advance the read cursor."""
        return self._bytes[self._i()] != 0

    def read_byte(self, signed: bool = True) -> int:
        """Read a byte value then advance the read cursor.

        :param signed: Whether the value should be interpreted as signed or unsigned.
        """
        return self._read_number('Bb'[signed], 1)

    def read_short(self, signed: bool = True) -> int:
        """Read a short int value (2 bytes) then advance the read cursor.

        :param signed: Whether the value should be interpreted as signed or unsigned.
        """
        return self._read_number('Hh'[signed], 2)

    def read_int(self, signed: bool = True) -> int:
        """Read an int value (4 bytes) then advance the read cursor.

        :param signed: Whether the value should be interpreted as signed or unsigned.
        """
        return self._read_number('Ii'[signed], 4)

    def read_long(self, signed: bool = True) -> int:
        """Read a long int value (8 bytes) then advance the read cursor.

        :param signed: Whether the value should be interpreted as signed or unsigned.
        """
        return self._read_number('Qq'[signed], 8)

    def read_float(self) -> float:
        """Read a single precision float value (4 bytes) then advance the read cursor."""
        return self._read_number('f', 4)

    def read_double(self) -> float:
        """Read a double precision float value (8 bytes) then advance the read cursor."""
        return self._read_number('d', 8)

    def _read_number(self, f: str, byte_size: int) -> int | float:
        i = self._i(byte_size)
        return struct.unpack('>' + f, self._bytes[i:i + byte_size])[0]

    def read_string(self) -> str:
        """Read a string value decoded as UTF-8 then advance the read cursor."""
        size = self.read_int(signed=False)
        i = self._i(size)
        return self._bytes[i:i + size].decode('UTF-8')

    def read_vector(self, as_ints: bool = False) -> pygame.Vector2:
        """Read a vector then advance the read cursor.

        :param as_ints: True to read coordinates as ints, false to read them as floats.
        :return: A vector.
        """
        if as_ints:
            x = self.read_long()
            y = self.read_long()
        else:
            x = self.read_double()
            y = self.read_double()
        return pygame.Vector2(x, y)

    def write_bool(self, b: bool):
        """Write a boolean at the end of this buffer.

        :param b: A boolean value.
        """
        self._bytes.append(b)

    def write_byte(self, i: int, signed: bool = True):
        """Write a byte value at the end of this buffer.

        :param i: An int value.
        :param signed: Whether the value should be written as signed or unsigned.
        """
        self._write_number(i, 'Bb'[signed])

    def write_short(self, i: int, signed: bool = True):
        """Write a short int (2 bytes) value at the end of this buffer.

        :param i: An int value.
        :param signed: Whether the value should be written as signed or unsigned.
        """
        self._write_number(i, 'Hh'[signed])

    def write_int(self, i: int, signed: bool = True):
        """Write an int value (4 bytes) at the end of this buffer.

        :param i: An int value.
        :param signed: Whether the value should be written as signed or unsigned.
        """
        self._write_number(i, 'Ii'[signed])

    def write_long(self, i: int, signed: bool = True):
        """Write a long int value (8 bytes) at the end of this buffer.

        :param i: An int value.
        :param signed: Whether the value should be written as signed or unsigned.
        """
        self._write_number(i, 'Qq'[signed])

    def write_float(self, f: float):
        """Write a single precision float value (4 bytes) at the end of this buffer.

        :param f: A float value.
        """
        self._write_number(f, 'f')

    def write_double(self, f: float):
        """Write a double precision float value (8 bytes) at the end of this buffer.

        :param f: A float value.
        """
        self._write_number(f, 'd')

    def _write_number(self, v: int | float, f: str):
        self._bytes.extend(struct.pack('>' + f, v))

    def write_string(self, s: str):
        """Write a string value encoded as UTF-8 at the end of this buffer.
        The length of the string is written as an int value (4 bytes) before the string’s bytes.

        :param s: A string value.
        """
        bytes_ = s.encode('UTF-8')
        byte_size = len(bytes_)
        self.write_int(byte_size, signed=False)
        # String size is written as a 4-byte unsigned int so prevent writing more than 2^32 - 1 bytes
        actual_length = min(byte_size, 0xffffffff)
        self._bytes.extend(bytes_[:actual_length])

    def write_vector(self, v: pygame.Vector2, as_ints: bool = False):
        """Write the coordinates of a vector at the end of this buffer.
        Each coordinate will take up 8 bytes for 16 bytes in total.

        :param v: A vector.
        :param as_ints: True to write coordinates as ints, false to write them as floats.
        :return:
        """
        if as_ints:
            self.write_long(int(v.x))
            self.write_long(int(v.y))
        else:
            self.write_double(float(v.x))
            self.write_double(float(v.y))

    def _i(self, n: int = 1):
        """Advance the read cursor by n steps then return its value before update."""
        i = self._read_index
        self._read_index += n
        return i


__all__ = [
    'ByteBuffer',
]
