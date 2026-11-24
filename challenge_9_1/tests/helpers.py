from pathlib import Path

from textadv.engine import Game
from textadv.output import BufferOutput
from textadv.world_loader import build_world, load_world

WORLD_PATH = Path(__file__).resolve().parent.parent / "data" / "world.json"

TINY_WORLD = {
    "title": "Tiny",
    "start": "hall",
    "rooms": {
        "hall": {
            "name": "Hall",
            "description": "A bare hall.",
            "items": ["red_ball", "blue_ball", "box", "statue"],
            "exits": {
                "north": "attic",
                "east": {"to": "vault", "requires": [{"flag": "open_sesame"}],
                         "blocked": "A wall of force blocks you."},
            },
        },
        "attic": {"name": "Attic", "description": "Dusty.", "exits": {"south": "hall"}},
        "vault": {"name": "Vault", "description": "Gold!", "exits": {"west": "hall"}},
    },
    "items": {
        "red_ball": {"name": "red ball", "aliases": ["ball"]},
        "blue_ball": {"name": "blue ball", "aliases": ["ball"]},
        "box": {"name": "wooden box", "aliases": ["box"], "container": True,
                "contents": ["gem"]},
        "gem": {"name": "gem"},
        "statue": {"name": "statue", "scenery": True},
    },
    "triggers": [
        {"verb": "say", "item": "statue", "effects": [
            {"set_flag": "open_sesame"}, {"say": "The statue winks."}]},
    ],
}


def tiny_game(**kwargs) -> Game:
    game = Game(build_world(TINY_WORLD), out=BufferOutput(), **kwargs)
    game.start()
    game.out.clear()
    return game


def real_game(**kwargs) -> Game:
    game = Game(load_world(WORLD_PATH), out=BufferOutput(), **kwargs)
    game.start()
    return game


def run(game: Game, line: str) -> str:
    game.out.clear()
    game.handle(line)
    return game.out.text
