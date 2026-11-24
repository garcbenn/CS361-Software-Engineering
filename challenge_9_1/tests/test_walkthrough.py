import unittest

from helpers import real_game, run

WALKTHROUGH = """
n
w
read note
take matches
open chest
take key
e
e
take lamp
light lamp
w
n
unlock door with key
n
up
light beacon
""".split("\n")


class WalkthroughTests(unittest.TestCase):
    def test_full_game(self):
        game = real_game()
        for line in filter(None, WALKTHROUGH):
            self.assertFalse(game.state.over, f"game ended early before {line!r}")
            run(game, line)
        self.assertTrue(game.state.won)
        self.assertEqual(game.state.score, game.world.max_score)
        self.assertIn("You have won", game.out.text)

    def test_puzzle_gates(self):
        game = real_game()
        for line in ("n", "n"):
            run(game, line)
        self.assertIn("locked fast", run(game, "n"))
        self.assertIn("need the right key", run(game, "open door"))

    def test_dark_stairs(self):
        game = real_game()
        for line in ("n", "w", "open chest", "take key", "e", "n", "unlock door", "in"):
            run(game, line)
        self.assertEqual(game.state.room, "stairs")
        self.assertIn("total darkness", run(game, "u"))

    def test_wrong_key(self):
        game = real_game()
        for line in ("n", "e", "take rusty key", "w", "n"):
            run(game, line)
        self.assertIn("too corroded", run(game, "unlock door with rusty key"))


if __name__ == "__main__":
    unittest.main()
