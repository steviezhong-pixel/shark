"""Entry point for the per-profile browser subprocess."""

import sys

from .browser import launch


def main() -> None:
    args = [a for a in sys.argv[1:] if a and not a.startswith("-")] or []
    if not args:
        print("usage: python -m core.launcher <profile_id>")
        sys.exit(2)
    launch(args[0])


if __name__ == "__main__":
    main()
