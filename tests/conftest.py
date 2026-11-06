"""Optional fake window backend for tests that do not render."""
import sys
import types


def pytest_addoption(parser):
    parser.addoption(
        "--no-gui", action="store_true",
        help="Disable pyglet window creation for non-rendering unit tests.",
    )


def pytest_configure(config):
    if not config.getoption("--no-gui"):
        return

    def disabled(*args, **kwargs):
        raise AssertionError("Graphics initialization disabled by --no-gui")

    class Window:
        __init__ = disabled

    pyglet = types.ModuleType("pyglet")
    pyglet.__path__ = []
    pyglet.options = {}
    pyglet.window = types.ModuleType("pyglet.window")
    pyglet.window.Window = Window
    pyglet.clock = types.ModuleType("pyglet.clock")
    pyglet.clock.schedule_interval = disabled
    pyglet.clock.unschedule = disabled
    pyglet.gl = types.ModuleType("pyglet.gl")
    pyglet.gl.Config = disabled
    for name in ("window", "clock", "gl"):
        sys.modules["pyglet." + name] = getattr(pyglet, name)
    sys.modules["pyglet"] = pyglet
