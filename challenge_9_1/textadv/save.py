"""Save and restore GameState as JSON."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .model import GameState, World

SAVE_VERSION = 1
_NAME_RE = re.compile(r"^[A-Za-z0-9_-]{1,40}$")


class SaveError(Exception):
    pass


def save_path(directory: Path, name: str | None) -> Path:
    name = name or "savegame"
    if not _NAME_RE.match(name):
        raise SaveError("Save names may only use letters, digits, '-' and '_'.")
    return directory / f"{name}.json"


def save_game(world: World, state: GameState, path: Path) -> None:
    payload = {"version": SAVE_VERSION, "world": world.title, "state": state.to_dict()}
    try:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except OSError as e:
        raise SaveError(f"Couldn't save: {e.strerror}.") from e


def load_game(world: World, path: Path) -> GameState:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as e:
        raise SaveError(f"There's no saved game called '{path.stem}'.") from e
    except (OSError, json.JSONDecodeError) as e:
        raise SaveError(f"Couldn't read that save file: {e}.") from e

    if payload.get("version") != SAVE_VERSION or payload.get("world") != world.title:
        raise SaveError("That save file is from a different game or version.")
    try:
        state = GameState.from_dict(payload["state"])
    except (KeyError, TypeError) as e:
        raise SaveError("That save file is damaged.") from e
    if state.room not in world.rooms or any(i not in world.items for i in state.locations):
        raise SaveError("That save file doesn't match this world.")
    return state
