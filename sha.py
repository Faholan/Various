"""Custom implementation of SHA-256."""

from typing import List

__all__ = ("sha",)

MODULUS = (1 << 32) - 1

K = (
    0x428A2F98,
    0x71374491,
    0xB5C0FBCF,
    0xE9B5DBA5,
    0x3956C25B,
    0x59F111F1,
    0x923F82A4,
    0xAB1C5ED5,
    0xD807AA98,
    0x12835B01,
    0x243185BE,
    0x550C7DC3,
    0x72BE5D74,
    0x80DEB1FE,
    0x9BDC06A7,
    0xC19BF174,
    0xE49B69C1,
    0xEFBE4786,
    0x0FC19DC6,
    0x240CA1CC,
    0x2DE92C6F,
    0x4A7484AA,
    0x5CB0A9DC,
    0x76F988DA,
    0x983E5152,
    0xA831C66D,
    0xB00327C8,
    0xBF597FC7,
    0xC6E00BF3,
    0xD5A79147,
    0x06CA6351,
    0x14292967,
    0x27B70A85,
    0x2E1B2138,
    0x4D2C6DFC,
    0x53380D13,
    0x650A7354,
    0x766A0ABB,
    0x81C2C92E,
    0x92722C85,
    0xA2BFE8A1,
    0xA81A664B,
    0xC24B8B70,
    0xC76C51A3,
    0xD192E819,
    0xD6990624,
    0xF40E3585,
    0x106AA070,
    0x19A4C116,
    0x1E376C08,
    0x2748774C,
    0x34B0BCB5,
    0x391C0CB3,
    0x4ED8AA4A,
    0x5B9CCA4F,
    0x682E6FF3,
    0x748F82EE,
    0x78A5636F,
    0x84C87814,
    0x8CC70208,
    0x90BEFFFA,
    0xA4506CEB,
    0xBEF9A3F7,
    0xC67178F2,
)

H = (
    0x6A09E667,
    0xBB67AE85,
    0x3C6EF372,
    0xA54FF53A,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
    0x5BE0CD19,
)


def _add(*args: int) -> int:
    """Add numbers modulo 2^32."""
    result = 0
    for x in args:
        result = (result + x) & MODULUS
    return result


def _pad(message: int) -> int:
    """Pad a message to blocks of 512 bits."""
    length = message.bit_length()
    padding_length = 512 - length - 64 - 1
    return (1 << (64 + padding_length) + length) << length


def _rotr(n: int, x: int) -> int:
    """ROTR SHA operator."""
    return (x >> n) | ((x << (32 - n)) & MODULUS)


def _ch(x: int, y: int, z: int) -> int:
    """Ch SHA operator."""
    return (x & y) ^ ((x ^ MODULUS) & z)


def _maj(x: int, y: int, z: int) -> int:
    """Maj SHA operator."""
    return (x & y) ^ (x & z) ^ (y & z)


def _Σ0(x: int) -> int:
    """Σ0 SHA operator."""
    return _rotr(2, x) ^ _rotr(13, x) ^ _rotr(22, x)


def _Σ1(x: int) -> int:
    """Σ1 SHA operator."""
    return _rotr(6, x) ^ _rotr(11, x) ^ _rotr(25, x)


def _σ0(x: int) -> int:
    """σ0 SHA operator."""
    return _rotr(7, x) ^ _rotr(18, x) ^ (x >> 3)


def _σ1(x: int) -> int:
    """σ1 SHA operator."""
    return _rotr(17, x) ^ _rotr(19, x) ^ (x >> 10)


def _repr(x: int) -> str:
    """64 bits representation of x."""
    raw = hex(x)[2:]
    return "0" * (8 - len(raw)) + raw


def sha(message: int) -> str:
    """Hash a message according to SHA-256."""
    if message < 0:
        raise ValueError("The message must be positive.")
    if message.bit_length() > 1 << 64:
        raise ValueError("Message too big.")

    message = _pad(message)

    list_h = H

    while message:
        list_w: List[int] = []
        for _ in range(16):
            list_w.append(message & MODULUS)
            message >>= 32

        for _ in range(48):
            list_w.append(
                _add(
                    _σ1(list_w[-2]),
                    list_w[-7],
                    _σ0(list_w[-15]),
                    list_w[-16],
                )
            )

        a, b, c, d, e, f, g, h = list_h

        for t in range(64):
            t1 = _add(h, _Σ1(e), _ch(e, f, g), K[t], list_w[t])
            t2 = _add(_Σ0(a) + _maj(a, b, c))
            h, g, f = g, f, e
            e = d + t1
            d, c, b = c, b, a
            a = t1 + t2

        list_h = (
            a + list_h[0],
            b + list_h[1],
            c + list_h[2],
            d + list_h[3],
            e + list_h[4],
            f + list_h[5],
            g + list_h[6],
            h + list_h[7],
        )

    return "".join(_repr(x) for x in list_h)
