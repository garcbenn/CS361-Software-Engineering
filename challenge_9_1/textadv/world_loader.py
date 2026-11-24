"""Load and validate a world file (JSON).

World file shape (see data/world.json for a full example):

{
  "title": "...", "intro": "...", "start": "<room id>", "max_score": 40,
  "inventory": ["<item id>", ...],             # optional starting items
  "synonyms": {"ignite": "light"},             # optional extra verb synonyms
  "rooms": {
    "<id>": {
      "name": "...", "description": "...",
      "items": ["<item id>", ...],
      "exits": {
        "north": "<room id>",
        "up": {"to": "<room id>", "requires": [<cond>...], "blocked": "..."}
      },
      "extras": [{"requires": [<cond>...], "text": "..."}]
    }
  },
  "items": {
    "<id>": {
      "name": "brass key", "aliases": ["key"], "description": "...",
      "portable": true, "scenery": false, "text": "<for read>",
      "container": false, "open": false, "contents": ["<item id>", ...],
      "extras": [...]
    }
  },
  "triggers": [
    {"verbs": ["unlock", "open"], "item": "door", "with": "key",
     "requires": [<cond>...], "effects": [<effect>...],
     "fail": "<said if requires fail>", "once": false}
  ],
  "events": [{"requires": [...], "effects": [...], "once": true}]
}

Triggers are tried in order; the first whose verb/items match and whose
requirements hold runs its effects.  If requirements fail and the trigger
has a "fail" message, that's shown and matching stops; otherwise the next
trigger is tried.  Conditions and effects are defined in conditions.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import conditions
from .model import (
    INVENTORY, Event, Exit, Extra, Item, Room, Trigger, World, in_loc, room_loc,
)
from .parser import CANONICAL_DIRECTIONS


class WorldError(Exception):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


def load_world(path: str | Path) -> World:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError as e:
        raise WorldError([f"can't read world file: {e}"]) from e
    except json.JSONDecodeError as e:
        raise WorldError([f"invalid JSON: {e}"]) from e
    return build_world(data)


def build_world(data: dict) -> World:
    return _Builder(data).build()


class _Builder:
    def __init__(self, data: dict):
        self.data = data
        self.problems: list[str] = []
        self.items: dict[str, Item] = {}
        self.rooms: dict[str, Room] = {}

    def problem(self, msg: str) -> None:
        self.problems.append(msg)

    def build(self) -> World:
        data = self.data
        for key in ("title", "start", "rooms"):
            if key not in data:
                self.problem(f"missing top-level '{key}'")
        if self.problems:
            raise WorldError(self.problems)

        for iid, d in data.get("items", {}).items():
            self.items[iid] = self.make_item(iid, d)
        for rid, d in data["rooms"].items():
            self.rooms[rid] = self.make_room(rid, d)

        locations, open_ = self.place_items()
        triggers = [self.make_trigger(i, d) for i, d in enumerate(data.get("triggers", []))]
        events = [self.make_event(i, d) for i, d in enumerate(data.get("events", []))]

        if data["start"] not in self.rooms:
            self.problem(f"start room '{data['start']}' doesn't exist")
        for room in self.rooms.values():
            for direction, ex in room.exits.items():
                where = f"room '{room.id}' exit '{direction}'"
                if direction not in CANONICAL_DIRECTIONS:
                    self.problem(f"{where}: unknown direction")
                if ex.target not in self.rooms:
                    self.problem(f"{where}: leads to unknown room '{ex.target}'")
                self.check_conditions(ex.requires, where)

        if self.problems:
            raise WorldError(self.problems)

        return World(
            title=data["title"],
            intro=data.get("intro", ""),
            start=data["start"],
            rooms=self.rooms,
            items=self.items,
            triggers=triggers,
            events=events,
            initial_locations=locations,
            initial_open=open_,
            synonyms=data.get("synonyms", {}),
            max_score=data.get("max_score", 0),
            trigger_verbs=frozenset(v for t in triggers for v in t.verbs),
        )

    # --- pieces ---------------------------------------------------------

    def make_extras(self, entries: list[dict], where: str) -> list[Extra]:
        extras = []
        for d in entries:
            requires = d.get("requires", [])
            self.check_conditions(requires, where)
            extras.append(Extra(requires, d.get("text", "")))
        return extras

    def make_item(self, iid: str, d: dict) -> Item:
        where = f"item '{iid}'"
        if "name" not in d:
            self.problem(f"{where}: missing 'name'")
        scenery = d.get("scenery", False)
        return Item(
            id=iid,
            name=d.get("name", iid),
            description=d.get("description", "You see nothing special."),
            aliases=[a.lower() for a in d.get("aliases", [])],
            portable=d.get("portable", not scenery),
            scenery=scenery,
            container=d.get("container", False),
            text=d.get("text"),
            article=d.get("article"),
            extras=self.make_extras(d.get("extras", []), where),
        )

    def make_room(self, rid: str, d: dict) -> Room:
        where = f"room '{rid}'"
        for key in ("name", "description"):
            if key not in d:
                self.problem(f"{where}: missing '{key}'")
        exits = {}
        for direction, spec in d.get("exits", {}).items():
            if isinstance(spec, str):
                exits[direction] = Exit(spec)
            else:
                exits[direction] = Exit(
                    spec.get("to", ""),
                    spec.get("requires", []),
                    spec.get("blocked", "You can't go that way."),
                )
        return Room(
            id=rid,
            name=d.get("name", rid),
            description=d.get("description", ""),
            exits=exits,
            extras=self.make_extras(d.get("extras", []), where),
        )

    def place_items(self) -> tuple[dict[str, str], set[str]]:
        locations: dict[str, str] = {}
        open_: set[str] = set()

        def place(iid: str, loc: str, where: str) -> None:
            if iid not in self.items:
                self.problem(f"{where}: unknown item '{iid}'")
            elif iid in locations:
                self.problem(f"item '{iid}' is placed in more than one spot")
            else:
                locations[iid] = loc

        for iid in self.data.get("inventory", []):
            place(iid, INVENTORY, "inventory")
        for rid, d in self.data["rooms"].items():
            for iid in d.get("items", []):
                place(iid, room_loc(rid), f"room '{rid}'")
        for iid, d in self.data.get("items", {}).items():
            contents = d.get("contents", [])
            if (contents or d.get("open")) and not self.items[iid].container:
                self.problem(f"item '{iid}': has contents/open but isn't a container")
            for cid in contents:
                place(cid, in_loc(iid), f"item '{iid}' contents")
            if d.get("open"):
                open_.add(iid)
        return locations, open_

    def make_trigger(self, index: int, d: dict) -> Trigger:
        where = f"trigger #{index + 1}"
        verbs = d.get("verbs") or ([d["verb"]] if "verb" in d else [])
        if not verbs:
            self.problem(f"{where}: needs 'verb' or 'verbs'")
        for key in ("item", "with"):
            if d.get(key) is not None and d[key] not in self.items:
                self.problem(f"{where}: unknown {key} '{d[key]}'")
        requires, effects = d.get("requires", []), d.get("effects", [])
        self.check_conditions(requires, where)
        self.check_effects(effects, where)
        return Trigger(
            id=f"t{index}",
            verbs=[v.lower() for v in verbs],
            item=d.get("item"),
            with_=d.get("with"),
            requires=requires,
            effects=effects,
            fail=d.get("fail"),
            once=d.get("once", False),
        )

    def make_event(self, index: int, d: dict) -> Event:
        where = f"event #{index + 1}"
        requires, effects = d.get("requires", []), d.get("effects", [])
        self.check_conditions(requires, where)
        self.check_effects(effects, where)
        return Event(f"e{index}", requires, effects, d.get("once", True))

    # --- validation -------------------------------------------------------

    def _single(self, entry, where: str, kind: str, table: dict):
        if not isinstance(entry, dict) or len(entry) != 1:
            self.problem(f"{where}: {kind} must be a one-key object, got {entry!r}")
            return None, None
        ((key, value),) = entry.items()
        if key not in table:
            self.problem(f"{where}: unknown {kind} '{key}'")
            return None, None
        return key, value

    def _ref(self, value, table: dict, what: str, where: str) -> None:
        if value not in table:
            self.problem(f"{where}: unknown {what} '{value}'")

    def check_conditions(self, conds: list, where: str) -> None:
        for cond in conds:
            key, value = self._single(cond, where, "condition", conditions.CONDITIONS)
            if key in conditions.CONDITION_ITEM_REFS:
                self._ref(value, self.items, "item", where)
            elif key in conditions.CONDITION_ROOM_REFS:
                self._ref(value, self.rooms, "room", where)

    def check_effects(self, effects: list, where: str) -> None:
        for effect in effects:
            key, value = self._single(effect, where, "effect", conditions.EFFECTS)
            if key in conditions.EFFECT_ITEM_REFS:
                self._ref(value, self.items, "item", where)
            elif key in conditions.EFFECT_ROOM_REFS:
                self._ref(value, self.rooms, "room", where)
            elif key == "move_item":
                if not isinstance(value, dict) or "item" not in value or "to" not in value:
                    self.problem(f"{where}: move_item needs 'item' and 'to'")
                    continue
                self._ref(value["item"], self.items, "item", where)
                self.check_location(value["to"], where)

    def check_location(self, loc: str, where: str) -> None:
        if loc in (INVENTORY, "here"):
            return
        kind, _, ident = loc.partition(":")
        if kind == "room":
            self._ref(ident, self.rooms, "room", where)
        elif kind == "item":
            self._ref(ident, self.items, "item", where)
        else:
            self.problem(f"{where}: bad location '{loc}' (use inv, here, room:<id>, item:<id>)")
