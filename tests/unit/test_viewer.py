"""Thread-startup tests; no native windows or OpenGL contexts are created."""
from concurrent.futures import ThreadPoolExecutor
import threading

import pytest

from pyribbit import Scene, Viewer
import pyribbit.viewer as viewer_module


def test_macos_rejects_threaded_viewer_before_initialization(monkeypatch):
    monkeypatch.setattr(viewer_module.sys, "platform", "darwin")
    with pytest.raises(RuntimeError, match="main thread"):
        Viewer(None, run_in_thread=True)


def test_macos_rejects_worker_thread_constructor(monkeypatch):
    monkeypatch.setattr(viewer_module.sys, "platform", "darwin")
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(Viewer, None, auto_start=False)
        with pytest.raises(RuntimeError, match="main thread"):
            future.result()


def test_macos_rejects_delayed_start_from_worker(monkeypatch):
    monkeypatch.setattr(viewer_module.sys, "platform", "darwin")
    viewer = Viewer(Scene(), auto_start=False)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(viewer.start)
        with pytest.raises(RuntimeError, match="main thread"):
            future.result()


def test_macos_allows_main_thread_and_deferred_start(monkeypatch):
    monkeypatch.setattr(viewer_module.sys, "platform", "darwin")
    calls = []

    def start(viewer):
        viewer_module._check_viewer_thread()
        calls.append(threading.current_thread())

    monkeypatch.setattr(Viewer, "_init_and_start_app", start)
    viewer = Viewer(Scene(), auto_start=False)
    assert calls == []
    viewer.start()
    Viewer(Scene())
    assert calls == [threading.main_thread(), threading.main_thread()]


@pytest.mark.parametrize("platform", ["linux", "win32"])
def test_other_platforms_keep_threaded_start(monkeypatch, platform):
    monkeypatch.setattr(viewer_module.sys, "platform", platform)
    calls = []

    def start(viewer):
        viewer_module._check_viewer_thread()
        calls.append(threading.current_thread())

    monkeypatch.setattr(Viewer, "_init_and_start_app", start)
    viewer = Viewer(Scene(), run_in_thread=True)
    viewer._thread.join(timeout=5)
    assert not viewer._thread.is_alive()
    assert calls == [viewer._thread]
    assert calls[0] is not threading.main_thread()
