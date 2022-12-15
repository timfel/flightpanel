from time import sleep as _sleep
from enum import IntEnum as _IntEnum


Key = _IntEnum(
    "Key",
    {
        "a": 0x04,
        "b": 0x05,
        "c": 0x06,
        "d": 0x07,
        "e": 0x08,
        "f": 0x09,
        "g": 0x0a,
        "h": 0x0b,
        "i": 0x0c,
        "j": 0x0d,
        "k": 0x0e,
        "l": 0x0f,
        "m": 0x10,
        "n": 0x11,
        "o": 0x12,
        "p": 0x13,
        "q": 0x14,
        "r": 0x15,
        "s": 0x16,
        "t": 0x17,
        "u": 0x18,
        "v": 0x19,
        "w": 0x1a,
        "x": 0x1b,
        "y": 0x1c,
        "z": 0x1d,
        "1": 0x1e,
        "2": 0x1f,
        "3": 0x20,
        "4": 0x21,
        "5": 0x22,
        "6": 0x23,
        "7": 0x24,
        "8": 0x25,
        "9": 0x26,
        "0": 0x27,
        "enter": 0x28,
        "escape": 0x29,
        "backspace": 0x2a,
        "tab": 0x2b,
        "spacebar": 0x2c,
        "-": 0x2d,
        ",": 0x36,
        ".": 0x37,
        "f1": 0x3a,
        "f2": 0x3b,
        "f3": 0x3c,
        "f4": 0x3d,
        "f5": 0x3e,
        "f6": 0x3f,
        "f7": 0x40,
        "f8": 0x41,
        "f9": 0x42,
        "f10": 0x43,
        "f11": 0x44,
        "f12": 0x45,
        "page up": 0x4b,
        "end": 0x4d,
        "page down": 0x4e,
        "right arrow": 0x4f,
        "left arrow": 0x50,
        "down arrow": 0x51,
        "up arrow": 0x52,
        "keypad /": 0x54,
        "keypad *": 0x55,
        "keypad -": 0x56,
        "keypad +": 0x57,
        "keypad enter": 0x58,
        "keypad 1": 0x59,
        "keypad 2": 0x5a,
        "keypad 3": 0x5b,
        "keypad 4": 0x5c,
        "keypad 5": 0x5d,
        "keypad 6": 0x5e,
        "keypad 7": 0x5f,
        "keypad 8": 0x60,
        "keypad 9": 0x61,
        "keypad 0": 0x62,
        "keypad .": 0x63,
    },
)


Modifier = _IntEnum(
    "Modifier",
    {
        "lctrl": 1,
        "lshift": 2,
        "lalt": 4,
        "lwin": 8,
        "rctrl": 16,
        "rshift": 32,
        "ralt": 64,
        "rwin": 128,
    },
)


class Keyboard:
    def __init__(self, test_mode=False):
        if not test_mode:
            self._hidfd = open("/dev/hidg0", "rb+")
        else:
            self._hidfd = open("test", "rb+")

    def send_key(self, key, modifiers=None):
        self._hidfd.write(bytearray([modifiers, 0, key, 0, 0, 0, 0, 0]))
        self._hidfd.flush()
        _sleep(0.2)
        self._hidfd.write(b"\0\0\0\0\0\0\0\0")
        self._hidfd.flush()
