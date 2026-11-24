#!/usr/bin/env python3
"""Play a text adventure in the terminal.

    python main.py                      # the bundled world
    python main.py --world other.json   # any other world file
"""

import argparse
import sys
from pathlib import Path

try:
    import readline  # noqa: F401  -- line editing and history where available
except ImportError:
    pass

from textadv.engine import Game
from textadv.world_loader import WorldError, load_world

DEFAULT_WORLD = Path(__file__).resolve().parent / "data" / "world.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Play a text adventure.")
    ap.add_argument("--world", type=Path, default=DEFAULT_WORLD, help="world file (JSON)")
    args = ap.parse_args(argv)

    try:
        world = load_world(args.world)
    except WorldError as e:
        print(f"Problems in {args.world}:", file=sys.stderr)
        for problem in e.problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    Game(world).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
