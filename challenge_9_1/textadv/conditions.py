"""The tiny condition/effect language used by world files.

Each condition and effect is a single-key dict:

    {"flag": "door_unlocked"}          {"set_flag": "door_unlocked"}
    {"has": "brass_key"}               {"say": "The lock clicks."}

Adding a new kind is just adding an entry to CONDITIONS or EFFECTS (and,
if it refers to an item or room, to the matching *_REFS set so the loader
can validate it).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .model import INVENTORY, Condition, Effect, room_loc

if TYPE_CHECKING:
    from .engine import Game


def _has(game: Game, item_id: str) -> bool:
    return game.state.locations.get(item_id) == INVENTORY


CONDITIONS = {
    "flag": lambda g, v: v in g.state.flags,
    "not_flag": lambda g, v: v not in g.state.flags,
    "has": _has,
    "not_has": lambda g, v: not _has(g, v),
    "in_room": lambda g, v: g.state.room == v,
    "is_open": lambda g, v: v in g.state.open,
    "visited": lambda g, v: v in g.state.visited,
}

CONDITION_ITEM_REFS = {"has", "not_has", "is_open"}
CONDITION_ROOM_REFS = {"in_room", "visited"}


def _location(game: Game, where: str) -> str:
    return room_loc(game.state.room) if where == "here" else where


def _move_item(game: Game, value: dict) -> None:
    game.state.locations[value["item"]] = _location(game, value["to"])


def _add_score(game: Game, points: int) -> None:
    game.state.score += points


EFFECTS = {
    "say": lambda g, v: g.say(v),
    "set_flag": lambda g, v: g.state.flags.add(v),
    "clear_flag": lambda g, v: g.state.flags.discard(v),
    "give": lambda g, v: g.state.locations.__setitem__(v, INVENTORY),
    "remove_item": lambda g, v: g.state.locations.pop(v, None),
    "move_item": _move_item,  # {"item": id, "to": "inv" | "here" | "room:x" | "item:x"}
    "move_player": lambda g, v: g.move_to(v),
    "open": lambda g, v: g.state.open.add(v),
    "close": lambda g, v: g.state.open.discard(v),
    "score": _add_score,
    "win": lambda g, v: g.end(v, won=True),
    "lose": lambda g, v: g.end(v, won=False),
}

EFFECT_ITEM_REFS = {"give", "remove_item", "open", "close"}
EFFECT_ROOM_REFS = {"move_player"}


def _split(entry: dict) -> tuple[str, object]:
    ((key, value),) = entry.items()
    return key, value


def check(game: Game, cond: Condition) -> bool:
    key, value = _split(cond)
    return CONDITIONS[key](game, value)


def check_all(game: Game, conds: list[Condition]) -> bool:
    return all(check(game, c) for c in conds)


def apply_all(game: Game, effects: list[Effect]) -> None:
    for effect in effects:
        key, value = _split(effect)
        EFFECTS[key](game, value)
