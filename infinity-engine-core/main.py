"""Infinity Lines - entry point.

Usage:
    python3 main.py                          # open the management UI
    python3 main.py --launch-profile <id>    # internal: launch a profile's browser
"""

import subprocess
import sys


def _cleanup_stale_resource_trackers() -> None:
    """Kill orphaned multiprocessing.resource_tracker processes from this app.

    Camoufox used to create a multiprocessing.Lock on every launch, which on
    macOS spawns a resource_tracker child that registers its own Dock icon and
    outlives the browser as a PPID=1 orphan.  New builds no longer spawn them;
    this clears leftovers from older builds.  Only runs when no launcher or
    browser is active, so a legitimate in-use tracker is never touched.
    """
    if sys.platform != "darwin":
        return
    try:
        active = subprocess.run(
            ["pgrep", "-f", r"Infinity Lines\.app.*(--launch-profile|Camoufox\.app/Contents/MacOS/camoufox)"],
            capture_output=True, text=True, timeout=5,
        ).stdout.split()
    except Exception:
        return
    if active:
        return
    try:
        out = subprocess.run(
            ["pgrep", "-f", r"Infinity Lines\.app.*multiprocessing\.resource_tracker"],
            capture_output=True, text=True, timeout=5,
        ).stdout.split()
    except Exception:
        return
    for pid in out:
        try:
            subprocess.run(["kill", pid], timeout=5)
        except Exception:
            pass


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--launch-profile":
        from core.launcher import main as launch
        launch()
        return
    _cleanup_stale_resource_trackers()
    from gui.app import run
    run()


if __name__ == "__main__":
    main()
