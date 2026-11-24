"""Built-in verbs.

Each handler takes (game, cmd).  By the time it runs, the engine has already
resolved cmd.noun / cmd.noun2 into cmd.item / cmd.item2 (for verbs with
nouns=True) and given world triggers first chance to handle the command.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .conditions import check_all
from .model import INVENTORY, Item, in_loc, room_loc
from .output import join_list
from .parser import CANONICAL_DIRECTIONS, Command
from .save import SaveError, load_game, save_game, save_path

if TYPE_CHECKING:
    from .engine import Game

Handler = Callable[["Game", Command], None]


@dataclass
class VerbSpec:
    name: str
    fn: Handler
    nouns: bool = True  # resolve nouns to items (and allow triggers)
    meta: bool = False  # doesn't take a game turn
    allow_all: bool = False  # accepts "all" as a noun


VERBS: dict[str, VerbSpec] = {}
ALIASES: dict[str, str] = {}


def verb(*names: str, nouns: bool = True, meta: bool = False, allow_all: bool = False):
    def register(fn: Handler) -> Handler:
        canonical = names[0]
        VERBS[canonical] = VerbSpec(canonical, fn, nouns, meta, allow_all)
        for name in names:
            ALIASES[name] = canonical
        return fn

    return register


def no_builtin(game: Game, cmd: Command) -> None:
    """Fallback for verbs that only exist in world triggers."""
    if cmd.item is None:
        game.say(f"{cmd.verb.capitalize()} what?")
    elif cmd.item2 is not None:
        game.say("That doesn't seem to work.")
    else:
        game.say(f"You can't {cmd.verb} {cmd.item.the_name}.")


def _need_item(game: Game, cmd: Command, verb_name: str) -> Item | None:
    if cmd.item is None:
        game.say(f"{verb_name} what?")
    return cmd.item


# --- looking ----------------------------------------------------------------

@verb("look", "l")
def look(game: Game, cmd: Command) -> None:
    if cmd.item:
        game.describe_item(cmd.item)
    else:
        game.describe_room(full=True)


@verb("examine", "x", "inspect", "check", "describe", "search")
def examine(game: Game, cmd: Command) -> None:
    if item := _need_item(game, cmd, "Examine"):
        game.describe_item(item)


@verb("read")
def read(game: Game, cmd: Command) -> None:
    if item := _need_item(game, cmd, "Read"):
        game.say(item.text or f"There's nothing written on {item.the_name}.")


@verb("inventory", "i", "inv", nouns=False, meta=True)
def inventory(game: Game, cmd: Command) -> None:
    carried = game.items_at(INVENTORY)
    if not carried:
        game.say("You are empty-handed.")
        return
    game.say("You are carrying:")
    for item in carried:
        game.say(f"  {item.a_name}")


# --- moving -----------------------------------------------------------------

@verb("go", "walk", "run", "move", nouns=False)
def go(game: Game, cmd: Command) -> None:
    if not cmd.noun:
        game.say("Go where?")
        return
    if cmd.noun not in CANONICAL_DIRECTIONS:
        game.say("That's not a direction I understand.")
        return
    exit_ = game.room.exits.get(cmd.noun)
    if exit_ is None:
        game.say("You can't go that way.")
    elif not check_all(game, exit_.requires):
        game.say(exit_.blocked)
    else:
        game.move_to(exit_.target)


# --- handling things --------------------------------------------------------

def _take_one(game: Game, item: Item) -> str:
    if game.holding(item):
        return "You already have that."
    if not item.portable:
        return "That's not something you can carry."
    game.state.locations[item.id] = INVENTORY
    return "Taken."


@verb("take", "get", "grab", "pick", allow_all=True)
def take(game: Game, cmd: Command) -> None:
    if cmd.noun == "all":
        here = [i for i in game.items_at(room_loc(game.state.room)) if i.portable]
        if not here:
            game.say("There's nothing here to take.")
        for item in here:
            game.say(f"{item.name}: {_take_one(game, item)}")
        return
    if item := _need_item(game, cmd, "Take"):
        game.say(_take_one(game, item))


@verb("drop", "discard", allow_all=True)
def drop(game: Game, cmd: Command) -> None:
    if cmd.noun == "all":
        carried = game.items_at(INVENTORY)
        if not carried:
            game.say("You aren't carrying anything.")
        for item in carried:
            game.state.locations[item.id] = room_loc(game.state.room)
            game.say(f"{item.name}: Dropped.")
        return
    if item := _need_item(game, cmd, "Drop"):
        if not game.holding(item):
            game.say("You aren't carrying that.")
        else:
            game.state.locations[item.id] = room_loc(game.state.room)
            game.say("Dropped.")


@verb("put", "place", "insert")
def put(game: Game, cmd: Command) -> None:
    item = _need_item(game, cmd, "Put")
    if item is None:
        return
    target = cmd.item2
    if target is None:
        game.say(f"Put {item.the_name} where?")
    elif not game.holding(item):
        game.say("You aren't carrying that.")
    elif target is item:
        game.say("That would be quite a trick.")
    elif not target.container or cmd.prep in ("on", "onto"):
        game.say(f"You can't put things {cmd.prep or 'in'} {target.the_name}.")
    elif not game.is_open(target):
        game.say(f"{target.the_name.capitalize()} is closed.")
    else:
        game.state.locations[item.id] = in_loc(target.id)
        game.say(f"You put {item.the_name} in {target.the_name}.")


@verb("open")
def open_(game: Game, cmd: Command) -> None:
    item = _need_item(game, cmd, "Open")
    if item is None:
        return
    if not item.container:
        game.say("That's not something you can open.")
    elif game.is_open(item):
        game.say("It's already open.")
    else:
        game.state.open.add(item.id)
        inside = game.contents(item)
        if inside:
            game.say(f"Opening {item.the_name} reveals {join_list([i.a_name for i in inside])}.")
        else:
            game.say(f"You open {item.the_name}. It's empty.")


@verb("close", "shut")
def close(game: Game, cmd: Command) -> None:
    item = _need_item(game, cmd, "Close")
    if item is None:
        return
    if not item.container:
        game.say("That's not something you can close.")
    elif not game.is_open(item):
        game.say("It's already closed.")
    else:
        game.state.open.discard(item.id)
        game.say("Closed.")


@verb("wait", "z", nouns=False)
def wait(game: Game, cmd: Command) -> None:
    game.say("Time passes.")


# --- meta -------------------------------------------------------------------

HELP_TEXT = """\
Type short commands, like:
  look (l)            examine (x) <thing>     read <thing>
  north (n), south (s), east (e), west (w), up (u), down (d), in, out
  take <thing>        take all                drop <thing>
  open <thing>        close <thing>           put <thing> in <thing>
  inventory (i)       wait (z)                score
  save [name]         load [name]             quit (q)
Other verbs (unlock, light, use ...) may work on the right things."""


@verb("help", "?", nouns=False, meta=True)
def help_(game: Game, cmd: Command) -> None:
    game.say(HELP_TEXT)


@verb("score", nouns=False, meta=True)
def score(game: Game, cmd: Command) -> None:
    game.say(game.score_line())


@verb("save", nouns=False, meta=True)
def save(game: Game, cmd: Command) -> None:
    try:
        path = save_path(game.save_dir, cmd.noun)
        save_game(game.world, game.state, path)
    except SaveError as e:
        game.say(str(e))
    else:
        game.say(f"Saved to {path.name}.")


@verb("load", "restore", nouns=False, meta=True)
def load(game: Game, cmd: Command) -> None:
    try:
        game.state = load_game(game.world, save_path(game.save_dir, cmd.noun))
    except SaveError as e:
        game.say(str(e))
        return
    game.last_item = None
    game.say("Game restored.")
    game.describe_room(full=True)


@verb("quit", "q", nouns=False, meta=True)
def quit_(game: Game, cmd: Command) -> None:
    game.say(game.score_line())
    game.say("Goodbye.")
    game.state.over = True
