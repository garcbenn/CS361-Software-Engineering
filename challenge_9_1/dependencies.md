
# In-Class Challenge 9.1: Dependencies

**Name:** Benny Garcia

## 1. Import Dependencies

Import dependencies happen when a module depends on code imported from another module or library.

### Standard Library Dependencies

- `main.py`: argparse, sys, pathlib, readline
- `commands.py`: __future__
- `conditions.py`: __future__
- `engine.py`: __future__, collections.abc, pathlib
- `model.py`: __future__, dataclasses
- `output.py`: __future__, shutil, textwrap, collections.abc
- `parser.py`: __future__, re, dataclasses, typing
- `save.py`: __future__, json, re, pathlib
- `world_loader.py`: __future__, json, pathlib
- `helpers.py`: pathlib
- `test_commands.py`: copy, tempfile, unittest, pathlib
- `test_parser.py`: unittest
- `test_walkthrough.py`: unittest

### Internal Project Dependencies

- `main.py` depends on `engine.py` and `world_loader.py`
- `commands.py` depends on `conditions.py`, `model.py`,
  `output.py`, `parser.py`, `save.py`, and `engine.py`
- `engine.py` depends on `commands.py`, `conditions.py`,
  `model.py`, `output.py`, and `parser.py`
- `model.py` has no internal import dependencies
- `output.py` has no internal import dependencies
- `parser.py` depends on `model.py`
- `save.py` depends on `model.py`

## 2. Class Dependencies

### Is-a Relationships

- `BufferOutput` is an `Output`
- `CommandTests` is a `unittest.TestCase`
- `WorldValidationTests` is a `unittest.TestCase`
- `ParserTests` is a `unittest.TestCase`
- `WalkthroughTests` is a `unittest.TestCase`

### Has-a Relationships

#### Game (engine.py)

- Has a `World` through `self.world`
- Has an `Output` through `self.out`
- Has a `GameState` through `self.state`
- Has a `Path` through `self.save_dir`
- Has an optional `Item` through `self.last_item`

#### World (model.py)

- Has a dictionary of `Room` objects
- Has a dictionary of `Item` objects
- Has a list of `Trigger` objects
- Has a list of `Event` objects

## 3. Data Dependencies

### World Data

The JSON file contains the main adventure data:

- Game title and introduction
- Starting room
- Maximum score
- Command synonyms
- Room definitions
- Item definitions
- Triggers
- Events

### World

The World class stores static game data, including:

- Rooms and exits
- Items and their properties
- Triggers and events
- Initial item locations
- Initially open containers
- Synonyms and trigger verbs
- Maximum score