"""Core modules.

When running from a PyInstaller bundle, point Playwright at the Chromium
browser bundled inside the app's Resources directory.
"""

import os
import sys


def _setup_browser_path():
    if getattr(sys, "frozen", False):
        macos_dir = os.path.dirname(sys.executable)
        resources = os.path.join(os.path.dirname(macos_dir), "Resources")
        candidate = os.path.join(resources, "ms-playwright")
        if os.path.isdir(candidate):
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = candidate


_setup_browser_path()
