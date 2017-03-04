from .i3wm import i3wm
from ._self import _self

prog_defs = []


def setup(Settings):
    global prog_defs
    prog_defs = [
        _self(Settings),
        i3wm(Settings),
    ]
