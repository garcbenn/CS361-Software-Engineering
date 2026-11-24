"""The Game: ties world, state, parser and commands together."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from . import commands
from .conditions import apply_all, check_all
from .model import INVENTORY, Extra, GameState, Item, World, in_loc, room_loc
from .output import Output, join_list
from .parser import Command, parse


class Game:
    def __init__(
        self,
        world: World,
        out: Output | None = None,
        state: GameState | None = None,
        save_dir: Path | None = None,
    ):
        self.world = world
        self.out = out or Output()
        self.state = state or world.new_state()
        self.save_dir = save_dir or Path.cwd()
        self.last_item: Item | None = None  # what "it" refers to

    # --- main loop ----------------------------------------------------------

    def start(self) -> None:
        self.say(self.world.title.upper())
        if self.world.intro:
            self.say()
            self.say(self.world.intro)
        self.say("(Type HELP for a list of commands.)")
        self.describe_room(full=True)

    def run(self, read: Callable[[str], str] = input) -> None:
        self.start()
        while not self.state.over:
            try:
                line = read("\n> ")
            except (EOFError, KeyboardInterrupt):
                self.say("\nGoodbye.")
                return
            self.handle(line)

    def handle(self, line: str) -> None:
        """Process one line of input."""
        cmd = parse(line)
        if cmd is None:
            self.say("Pardon?")
            return

        verb = self.world.synonyms.get(cmd.verb, cmd.verb)
        verb = commands.ALIASES.get(verb, verb)
        cmd.verb = verb
        spec = commands.VERBS.get(verb)
        if spec is None and verb not in self.world.trigger_verbs:
            self.say(f'I don\'t know how to "{verb}".')
            return

        takes_turn = not (spec and spec.meta)
        if takes_turn:
            self.state.turns += 1

        if spec is None or spec.nouns:
            if not self.resolve_nouns(cmd, allow_all=spec is not None and spec.allow_all):
                return
            handled = self.fire_triggers(cmd)
        else:
            handled = False

        if not handled:
            (spec.fn if spec else commands.no_builtin)(self, cmd)

        if takes_turn:
            self.run_events()

    # --- nouns ----------------------------------------------------------------

    def resolve_nouns(self, cmd: Command, allow_all: bool = False) -> bool:
        """Fill in cmd.item / cmd.item2.  Returns False (after explaining
        why) if a noun couldn't be matched to exactly one thing."""
        if cmd.noun and not (allow_all and cmd.noun == "all"):
            cmd.item = self.resolve(cmd.noun)
            if cmd.item is None:
                return False
        if cmd.noun2:
            cmd.item2 = self.resolve(cmd.noun2)
            if cmd.item2 is None:
                return False
        self.last_item = cmd.item2 or cmd.item or self.last_item
        return True

    def resolve(self, phrase: str) -> Item | None:
        scope = self.in_scope()
        if phrase in ("it", "them"):
            if self.last_item in scope:
                return self.last_item
            self.say("I'm not sure what you're referring to.")
            return None

        exact = [i for i in scope if phrase == i.name or phrase in i.aliases]
        if len(exact) == 1:
            return exact[0]
        words = phrase.split()
        candidates = exact or [i for i in scope if all(w in i.vocabulary for w in words)]
        if not candidates:
            self.say(f"You don't see any {phrase} here.")
            return None
        if len(candidates) == 1:
            return candidates[0]
        names = join_list([c.the_name for c in candidates], "or")
        self.say(f"Which do you mean, {names}?")
        return None

    # --- queries --------------------------------------------------------------

    @property
    def room(self):
        return self.world.rooms[self.state.room]

    def items_at(self, loc: str) -> list[Item]:
        return [self.world.items[i] for i, where in self.state.locations.items() if where == loc]

    def contents(self, container: Item) -> list[Item]:
        return self.items_at(in_loc(container.id))

    def is_open(self, item: Item) -> bool:
        return item.id in self.state.open

    def holding(self, item: Item) -> bool:
        return self.state.locations.get(item.id) == INVENTORY

    def in_scope(self) -> list[Item]:
        """Items the player can refer to: in the room, carried, or inside an
        open container that is itself in scope."""
        found: list[Item] = []
        frontier = self.items_at(room_loc(self.state.room)) + self.items_at(INVENTORY)
        while frontier:
            item = frontier.pop(0)
            found.append(item)
            if item.container and self.is_open(item):
                frontier.extend(self.contents(item))
        return found

    def with_extras(self, base: str, extras: list[Extra]) -> str:
        parts = [base] + [e.text for e in extras if check_all(self, e.requires)]
        return " ".join(p for p in parts if p)

    # --- actions used by commands and effects ---------------------------------

    def say(self, text: str = "") -> None:
        self.out.say(text)

    def move_to(self, room_id: str) -> None:
        self.state.room = room_id
        self.describe_room(full=room_id not in self.state.visited)

    def end(self, message: str, won: bool) -> None:
        self.say(message)
        self.state.over = True
        self.state.won = won
        self.say()
        self.say(self.score_line())

    def score_line(self) -> str:
        s = self.state
        out_of = f" out of {self.world.max_score}" if self.world.max_score else ""
        turns = "turn" if s.turns == 1 else "turns"
        return f"Your score is {s.score}{out_of}, in {s.turns} {turns}."

    def describe_room(self, full: bool = True) -> None:
        room = self.room
        self.say()
        self.say(room.name)
        if full:
            self.say(self.with_extras(room.description, room.extras))

        here = self.items_at(room_loc(room.id))
        loose = [i.a_name for i in here if not i.scenery]
        if loose:
            self.say(f"You see {join_list(loose)} here.")
        for item in here:
            if item.container and self.is_open(item) and self.contents(item):
                inside = join_list([c.a_name for c in self.contents(item)])
                self.say(f"The {item.name} contains {inside}.")

        if room.exits:
            self.say(f"Exits: {', '.join(room.exits)}.")
        self.state.visited.add(room.id)

    def describe_item(self, item: Item) -> None:
        self.say(self.with_extras(item.description, item.extras))
        if item.container:
            if not self.is_open(item):
                self.say(f"The {item.name} is closed.")
            elif inside := self.contents(item):
                self.say(f"The {item.name} contains {join_list([c.a_name for c in inside])}.")
            else:
                self.say(f"The {item.name} is empty.")

    # --- scripting -------------------------------------------------------------

    def fire_triggers(self, cmd: Command) -> bool:
        item_id = cmd.item.id if cmd.item else None
        with_id = cmd.item2.id if cmd.item2 else None
        for trig in self.world.triggers:
            if cmd.verb not in trig.verbs or trig.item != item_id:
                continue
            if trig.with_ is not None and with_id not in (None, trig.with_):
                continue
            if trig.once and trig.id in self.state.fired:
                continue
            if not check_all(self, trig.requires):
                if trig.fail:
                    self.say(trig.fail)
                    return True
                continue
            self.state.fired.add(trig.id)
            apply_all(self, trig.effects)
            return True
        return False

    def run_events(self) -> None:
        for event in self.world.events:
            if self.state.over:
                return
            if event.once and event.id in self.state.fired:
                continue
            if check_all(self, event.requires):
                self.state.fired.add(event.id)
                apply_all(self, event.effects)
