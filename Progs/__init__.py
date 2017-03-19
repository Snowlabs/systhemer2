from .i3wm import i3wm
from ._self import _self
from . import common

prog_defs = []


def setup(Settings):
    """initializes the prog_defs array"""
    global prog_defs

    prog_defs = [
        _self(Settings),
        i3wm(Settings),
    ]
    common.Settings = Settings
