"""Turn a line of player input into a Command.

The parser only deals with words; matching nouns to actual items happens in
the engine, because that depends on what's in scope.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import Item

CANONICAL_DIRECTIONS = (
    "north", "south", "east", "west",
    "northeast", "northwest", "southeast", "southwest",
    "up", "down", "in", "out",
)

DIRECTIONS = {d: d for d in CANONICAL_DIRECTIONS} | {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down",
}

# One-word commands that mean movement.
MOVE_WORDS = {"enter": "in", "exit": "out", "leave": "out"}

ABBREVIATIONS = {
    "x": "examine",
    "i": "inventory",
    "inv": "inventory",
    "l": "look",
    "z": "wait",
    "q": "quit",
}

VERB_PHRASES = {
    ("pick", "up"): "take",
    ("look", "at"): "examine",
    ("look", "in"): "examine",
    ("look", "inside"): "examine",
    ("put", "down"): "drop",
}

ARTICLES = {"the", "a", "an", "some"}

PREPOSITIONS = {
    "with", "using", "in", "into", "inside", "on", "onto",
    "to", "at", "from", "under",
}

_PUNCT = re.compile(r"[^\w\s-]")


@dataclass
class Command:
    verb: str
    noun: str | None = None
    prep: str | None = None
    noun2: str | None = None
    # Filled in by the engine after resolving nouns against what's in scope.
    item: Item | None = None
    item2: Item | None = None


def parse(line: str) -> Command | None:
    words = _PUNCT.sub(" ", line.lower()).split()
    if not words:
        return None

    if len(words) == 1:
        word = words[0]
        if word in DIRECTIONS:
            return Command("go", DIRECTIONS[word])
        if word in MOVE_WORDS:
            return Command("go", MOVE_WORDS[word])

    if tuple(words[:2]) in VERB_PHRASES:
        verb, rest = VERB_PHRASES[tuple(words[:2])], words[2:]
    else:
        verb, rest = ABBREVIATIONS.get(words[0], words[0]), words[1:]

    rest = [w for w in rest if w not in ARTICLES]

    if verb == "go" and rest and rest[0] in DIRECTIONS:
        return Command("go", DIRECTIONS[rest[0]])

    # Split "unlock door with brass key" at the first preposition.
    for i, word in enumerate(rest):
        if word in PREPOSITIONS and i > 0:
            noun2 = " ".join(rest[i + 1:]) or None
            return Command(verb, " ".join(rest[:i]), word, noun2)

    return Command(verb, " ".join(rest) or None)
