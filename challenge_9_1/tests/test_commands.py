import copy
import tempfile
import unittest
from pathlib import Path

from textadv.model import INVENTORY
from textadv.world_loader import WorldError, build_world

from helpers import TINY_WORLD, run, tiny_game


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.game = tiny_game()

    def where(self, item_id):
        return self.game.state.locations.get(item_id)

    def test_unknown_verb(self):
        self.assertIn("don't know how", run(self.game, "frobnicate ball"))

    def test_ambiguous_noun(self):
        out = run(self.game, "take ball")
        self.assertIn("Which do you mean, the red ball or the blue ball?", out)
        self.assertEqual(self.where("red_ball"), "room:hall")

    def test_take_and_drop(self):
        self.assertIn("Taken.", run(self.game, "take red ball"))
        self.assertEqual(self.where("red_ball"), INVENTORY)
        self.assertIn("red ball", run(self.game, "i"))
        # Only one "ball" is in the room now, but both are in scope.
        self.assertIn("Which do you mean", run(self.game, "drop ball"))
        self.assertIn("Dropped.", run(self.game, "drop red"))
        self.assertEqual(self.where("red_ball"), "room:hall")

    def test_take_all_skips_scenery(self):
        run(self.game, "take all")
        self.assertEqual(self.where("red_ball"), INVENTORY)
        self.assertEqual(self.where("statue"), "room:hall")

    def test_pronoun(self):
        run(self.game, "x red ball")
        self.assertIn("Taken.", run(self.game, "take it"))

    def test_container_scope(self):
        self.assertIn("don't see any gem", run(self.game, "take gem"))
        self.assertIn("reveals a gem", run(self.game, "open box"))
        self.assertIn("Taken.", run(self.game, "take gem"))
        self.assertIn("You put the gem in the wooden box.", run(self.game, "put gem in box"))
        self.assertEqual(self.where("gem"), "item:box")

    def test_blocked_exit_and_trigger(self):
        self.assertIn("wall of force", run(self.game, "e"))
        self.assertIn("You can't go that way.", run(self.game, "w"))
        self.assertIn("winks", run(self.game, "say statue"))
        self.assertIn("Vault", run(self.game, "e"))

    def test_brief_description_on_revisit(self):
        self.assertIn("Dusty.", run(self.game, "n"))
        run(self.game, "s")
        self.assertNotIn("Dusty.", run(self.game, "n"))
        self.assertIn("Dusty.", run(self.game, "look"))

    def test_meta_commands_take_no_turn(self):
        run(self.game, "i")
        run(self.game, "help")
        self.assertEqual(self.game.state.turns, 0)
        run(self.game, "wait")
        self.assertEqual(self.game.state.turns, 1)

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = tiny_game(save_dir=Path(tmp))
            run(game, "take red ball")
            self.assertIn("Saved", run(game, "save slot1"))
            run(game, "drop red ball")
            run(game, "n")
            self.assertIn("restored", run(game, "load slot1"))
            self.assertEqual(game.state.room, "hall")
            self.assertEqual(game.state.locations["red_ball"], INVENTORY)
            self.assertIn("no saved game", run(game, "load nope"))
            self.assertIn("may only use", run(game, "save my game"))


class WorldValidationTests(unittest.TestCase):
    def test_reports_problems(self):
        data = copy.deepcopy(TINY_WORLD)
        data["rooms"]["hall"]["exits"]["west"] = "nowhere"
        data["rooms"]["attic"]["items"] = ["ghost", "gem"]
        data["triggers"].append({"verb": "x", "effects": [{"explode": True}]})
        with self.assertRaises(WorldError) as ctx:
            build_world(data)
        text = "\n".join(ctx.exception.problems)
        self.assertIn("unknown room 'nowhere'", text)
        self.assertIn("unknown item 'ghost'", text)
        self.assertIn("'gem' is placed in more than one spot", text)
        self.assertIn("unknown effect 'explode'", text)


if __name__ == "__main__":
    unittest.main()
