"""Data model.

Static definitions (World, Room, Item, Trigger, ...) are loaded once from the
world file and never modified.  Everything that changes during play lives in
GameState, which is what gets saved and restored.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields

# Item location strings used in GameState.locations:
#   "inv"          -> carried by the player
#   "room:<id>"    -> lying in a room
#   "item:<id>"    -> inside a container item
INVENTORY = "inv"


def room_loc(room_id: str) -> str:
    return f"room:{room_id}"


def in_loc(item_id: str) -> str:
    return f"item:{item_id}"


# Conditions and effects are single-key dicts, e.g. {"flag": "door_open"}.
Condition = dict
Effect = dict


@dataclass
class Exit:
    target: str
    requires: list[Condition] = field(default_factory=list)
    blocked: str = "You can't go that way."


@dataclass
class Extra:
    """Extra description text shown only while its conditions hold."""

    requires: list[Condition]
    text: str


@dataclass
class Room:
    id: str
    name: str
    description: str
    exits: dict[str, Exit] = field(default_factory=dict)
    extras: list[Extra] = field(default_factory=list)


@dataclass
class Item:
    id: str
    name: str
    description: str = "You see nothing special."
    aliases: list[str] = field(default_factory=list)
    portable: bool = True
    scenery: bool = False  # described in room text; not listed separately
    container: bool = False
    text: str | None = None  # what "read" shows
    article: str | None = None  # override "a"/"an" (e.g. "some", or "")
    extras: list[Extra] = field(default_factory=list)

    @property
    def a_name(self) -> str:
        art = self.article
        if art is None:
            art = "an" if self.name[:1].lower() in "aeiou" else "a"
        return f"{art} {self.name}" if art else self.name

    @property
    def the_name(self) -> str:
        return f"the {self.name}"

    @property
    def vocabulary(self) -> set[str]:
        words = set(self.name.split())
        for alias in self.aliases:
            words.update(alias.split())
        return words


@dataclass
class Trigger:
    """A scripted response to a verb applied to an item.

    Matches when the verb is in `verbs`, the direct object is `item`, and
    (if `with_` is set) the indirect object is `with_` or omitted.
    """

    id: str
    verbs: list[str]
    item: str | None
    with_: str | None
    requires: list[Condition]
    effects: list[Effect]
    fail: str | None = None
    once: bool = False


@dataclass
class Event:
    """Checked after every turn; fires when its conditions hold."""

    id: str
    requires: list[Condition]
    effects: list[Effect]
    once: bool = True


@dataclass
class World:
    title: str
    intro: str
    start: str
    rooms: dict[str, Room]
    items: dict[str, Item]
    triggers: list[Trigger]
    events: list[Event]
    initial_locations: dict[str, str]
    initial_open: set[str]
    synonyms: dict[str, str] = field(default_factory=dict)
    max_score: int = 0
    trigger_verbs: frozenset[str] = frozenset()

    def new_state(self) -> GameState:
        return GameState(
            room=self.start,
            locations=dict(self.initial_locations),
            open=set(self.initial_open),
        )


@dataclass
class GameState:
    room: str
    locations: dict[str, str]
    open: set[str] = field(default_factory=set)
    flags: set[str] = field(default_factory=set)
    visited: set[str] = field(default_factory=set)
    fired: set[str] = field(default_factory=set)
    turns: int = 0
    score: int = 0
    over: bool = False
    won: bool = False

    _SET_FIELDS = ("open", "flags", "visited", "fired")

    def to_dict(self) -> dict:
        data = asdict(self)
        for name in self._SET_FIELDS:
            data[name] = sorted(data[name])
        return data

    @classmethod
    def from_dict(cls, data: dict) -> GameState:
        kwargs = {f.name: data[f.name] for f in fields(cls) if f.name in data}
        for name in cls._SET_FIELDS:
            kwargs[name] = set(kwargs.get(name, ()))
        return cls(**kwargs)
