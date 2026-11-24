# AGENTS.md

A console (dumb-terminal) text adventure in Python. A generic engine runs
whatever world is described in a JSON file; the bundled game is
`data/world.json` ("The Last Light").

## Commands

```sh
python main.py                         # play the bundled world
python main.py --world path/to/w.json  # play another world
python -m unittest discover tests      # run all tests (from repo root)
```

- Python 3.14 (see `.devcontainer/`). **Standard library only**: no third-party
  dependencies, no `requirements.txt`. Keep it that way unless asked.
- I/O is plain `input()`/`print()`. Don't use curses, ANSI colors or cursor
  control; it has to work on a dumb terminal.
- Tests import `helpers` from `tests/` and `textadv` from the root, so run them
  from the repo root using the command above.

## Layout

| Path | Role |
|---|---|
| `main.py` | CLI entry: parses args, loads the world, runs `Game.run()` |
| `textadv/model.py` | Dataclasses. Static: `World`, `Room`, `Item`, `Exit`, `Trigger`, `Event`, `Extra`. Mutable: `GameState` |
| `textadv/parser.py` | Text → `Command(verb, noun, prep, noun2)`. Words only; it knows nothing about items |
| `textadv/engine.py` | `Game`: the main loop, noun resolution/scope, room/item description, trigger and event dispatch |
| `textadv/commands.py` | Built-in verbs, registered with the `@verb(...)` decorator |
| `textadv/conditions.py` | Condition/effect tables used by world files |
| `textadv/world_loader.py` | JSON → `World`, plus validation. **Its module docstring is the world-file format reference** |
| `textadv/save.py` | Save/load of `GameState` as JSON |
| `textadv/output.py` | `Output.say()` (wrapping), `BufferOutput` for tests, `join_list` |
| `tests/` | Parser, command, validation and full-walkthrough tests |

## Core design rules

1. **Content goes in data, not code.** Never special-case a room or item id in
   Python. If a puzzle needs new behavior, add a generic condition or effect
   (or a generic verb) and use it from the world file.
2. **All mutable state lives in `GameState`.** `World` and its objects are
   read-only after loading. Anything that changes during play must be a
   `GameState` field, or save/load will silently lose it. If you add a `set`
   field, add it to `GameState._SET_FIELDS` so it serializes.
3. **Item locations are strings** in `GameState.locations`: `"inv"`,
   `"room:<id>"` or `"item:<container id>"`. Use the `INVENTORY`, `room_loc()`
   and `in_loc()` helpers rather than building these strings by hand.
4. **All player-visible text goes through `game.say()`**, never `print()`. This
   is what makes the game testable and keeps text wrapped.
5. **Validate at load time.** Anything a world author can get wrong (bad ids,
   unknown keys) should be reported as a `WorldError` problem by
   `world_loader`, not discovered as a crash mid-game. The loader collects
   every problem and reports them together; it doesn't stop at the first.

## How a command flows

`Game.handle(line)`:
1. `parse()` produces a `Command`. Empty input prints "Pardon?".
2. Canonicalize the verb: world `synonyms` first, then `commands.ALIASES`.
3. If the verb is neither a built-in nor used by any trigger, reply "I don't
   know how to …".
4. Non-meta verbs increment `state.turns`.
5. For verbs with `nouns=True` (and trigger-only verbs), resolve the nouns
   against the items in scope into `cmd.item` / `cmd.item2`. On failure the
   game has already explained why, so stop.
6. **Triggers get first chance**, tried in file order. A built-in handler only
   runs if no trigger handled the command. Trigger-only verbs fall back to
   `commands.no_builtin`.
7. Non-meta commands then run the world `events`.

Trigger matching details: the verb must be in `verbs`, and `item` must equal the
direct object. If `with` is set, the indirect object may be omitted or must
equal it. If `with` is unset, any indirect object matches. When `requires` fails,
a `fail` message ends matching; with no `fail`, the next trigger is tried. The
world file relies on this ordering to layer its fallbacks: put the specific
case first and the generic message last.

## Common tasks

**Add a built-in verb.** In `commands.py`:
```python
@verb("push", "shove")            # first name is canonical; the rest are aliases
def push(game, cmd): ...
```
Flags:
- `nouns=False`: the verb doesn't take items (go/save/help) and skips triggers.
- `meta=True`: the verb doesn't use a turn.
- `allow_all=True`: the verb accepts the noun `all`.

Update `HELP_TEXT` too. Prefer world triggers for verbs that only matter for
specific objects.

**Add a condition or effect.** Add an entry to `CONDITIONS` or `EFFECTS` in
`conditions.py`. If its value is an item or room id, also add the key to the
matching `*_ITEM_REFS` / `*_ROOM_REFS` set so the loader validates it. If the
value has a more complex shape, add a check in `_Builder.check_effects`. Then
document it in the `world_loader.py` docstring.

**Change the world.** Edit `data/world.json`. If you change the solution path,
the score or `max_score`, update `WALKTHROUGH` in `tests/test_walkthrough.py`.
That test asserts a win with exactly `max_score` points.

**Change the parser.** Note that it lowercases input and strips punctuation
(apostrophes included, so `keeper's` → `keeper s`), drops articles, and treats
lone direction words as `go`. `in` is both a direction and a preposition: it
means a direction only as the first word. Add a `test_parser.py` case for any
new phrasing.

## Testing conventions

- Use `tests/helpers.py`:
  - `tiny_game()` builds a minimal inline world (`TINY_WORLD`) for unit tests.
  - `real_game()` loads `data/world.json`.
  - `run(game, line)` returns only the output of that command.
- Prefer feeding commands through `game.handle()`/`run()` over calling handlers
  directly. That way you exercise parsing, resolution and triggers too.
- `BufferOutput` wraps at 70 columns, so assert on short phrases that won't
  straddle a line break.
- Save/load tests must pass `save_dir=` a temporary directory. The default is
  the current working directory.

## Gotchas

- Save names are restricted to `[A-Za-z0-9_-]{1,40}`. A save records the world
  title and version, and loading rejects a mismatch, so renaming a world's
  `title` invalidates existing saves.
- Trigger and event ids (`t0`, `e0`, …) are list indices stored in
  `state.fired`. Reordering triggers or events can confuse saves from older
  versions of a world.
- Noun ambiguity is resolved by asking ("Which do you mean, …?"). There is no
  follow-up state; the player simply retypes. `take`/`drop` don't yet prefer
  items that aren't held / are held.
- `scenery` items are described in the room text and never listed. They default
  to `portable: false`. Open containers still list their contents, even when
  the container itself is scenery.
