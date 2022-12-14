try:
    import RPi.GPIO as GPIO
except ImportError:
    print("Test mode without GPIO")
    import random

    class GPIO:
        BOARD = IN = PUD_UP = PUD_DOWN = 1

        @staticmethod
        def setup(*args, **kwargs):
            ...

        @staticmethod
        def setmode(*args, **kwargs):
            ...

        @staticmethod
        def input(*args, **kwargs):
            return random.randint(1, 20) == 1


import hid
from itertools import cycle, zip_longest


class Switch:
    def __init__(self, gpio, on_key, off_key=None, on_pulls_down=True, name=""):
        self.name = name
        self.gpio = gpio
        self.on_key = self._parse_key(on_key)
        if off_key:
            self.off_key = self._parse_key(off_key)
        else:
            self.off_key = None
        GPIO.setup(
            gpio, GPIO.IN, pull_up_down=GPIO.PUD_UP if on_pulls_down else GPIO.PUD_DOWN
        )
        self.on = GPIO.input(gpio)
        self.on_pulls_down = on_pulls_down
        if on_pulls_down:
            self.on = not self.on

    def _parse_key(self, keystr):
        keystr_parts = keystr.split("+")
        mod = 0
        try:
            key = hid.Key[keystr_parts.pop().strip().lower()]
            for m in keystr_parts:
                mod |= hid.Modifier[m.strip().lower()]
        except KeyError as e:
            raise KeyError(f"Unknown key {e.args[0]}")
        return key, mod

    def check(self, keyboard):
        on = GPIO.input(self.gpio)
        if on is not self.on:
            self.on = on
            if on:
                keyboard.send_key(self.on_key[0], modifiers=self.on_key[1])
            elif self.off_key:
                keyboard.send_key(self.off_key[0], modifiers=self.on_key[1])

    def __repr__(self):
        r = ["["]
        if self.on_pulls_down:
            on, off = "-", "+"
        else:
            on, off = "+", "-"
        if self.name:
            r.append(self.name)
        r.append(f"({gpio})")
        r.append(f"{on}{self.on_key}")
        if self.off_key:
            r.append(f"{off}{self.off_key}")
        r.append("]")
        return " ".join(r)


class SwitchPanel:
    def __init__(self, *switches):
        GPIO.setmode(GPIO.BOARD)
        self.keyboard = hid.Keyboard(test_mode=hasattr(GPIO, "BCM"))
        self.switches = switches

    def run(self):
        print("Running panel:", self, sep="\n")
        for switch in cycle(self.switches):
            switch.check(self.keyboard)

    def __repr__(self):
        r = ["-- Switch Panel --"]
        for s1, s2, s3 in zip_longest(
            self.switches[::3], self.switches[1::3], self.switches[2::3], fillvalue=""
        ):
            r.append(f"{s1} {s2} {s3}")
        r.append("-" * len(r[0]))
        return "\n".join(r)


if __name__ == "__main__":
    # Specific config for my board

    import os
    import sys
    from argparse import ArgumentParser
    from configparser import ConfigParser

    default_config = {
        "button 1": "a",
        "button 2": "b",
        "button 3": "c",
        "pressure switch 1": "d/lshift+d",
        "pressure switch 2": "e/lshift+e",
        "pressure switch 3": "f/lshift+f",
        "pressure switch 4": "g/lshift+g",
        "pressure switch 5": "h/lshift+h",
        "pressure switch 6": "i/lshift+i",
        "toggle switch 1": "j/lshift+j",
        "toggle switch 2": "k/lshift+k",
        "toggle switch 3": "l/lshift+l",
        "toggle switch 4": "m/lshift+m",
        "toggle switch 5": "n/lshift+n",
        "toggle switch 6": "o/lshift+o",
        "4 position knob": "1/0, 2, 3",
        "kill switch": "q",
    }
    gpios = [7, 8, 10, 11, 12, 13, 15, 16, 18, 22, 29, 31, 32, 33, 35, 36, 37, 38, 40]
    assert len(gpios) == len(default_config) + 2

    parser = ArgumentParser()
    parser.add_argument("configfile")
    args = parser.parse_args(sys.argv[1:])
    config = ConfigParser()
    if not os.path.exists(args.configfile):
        # create default config
        config["Default"] = default_config
        config["Available Keys"] = {k:"" for k in hid.Key.__members__.keys()}
        config["Available Modifiers"] = {k:"" for k in hid.Modifier.__members__.keys()}
        with open(args.configfile, "w") as configfile:
            config.write(configfile)
    else:
        config.read(args.configfile)

    switches = []
    for switch, config in config["Default"].items():
        switch = switch.lower()
        gpio = gpios[list(default_config.keys()).index(switch)]
        for idx, swconfig in enumerate(config.split(",")):
            keys = swconfig.strip().split("/")
            on_key = keys[0].strip().lower()
            off_key = keys[1].strip().lower() if len(keys) > 1 else None
            switches.append(
                Switch(
                    gpio,
                    on_key,
                    off_key,
                    on_pulls_down=(not switch.startswith("toggle switch")),
                    name=f"{switch}#{idx + 1}",
                )
            )

    p = SwitchPanel(*switches)
    p.run()
