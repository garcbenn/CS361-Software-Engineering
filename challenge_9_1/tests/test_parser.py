import unittest

from textadv.parser import Command, parse


class ParserTests(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(parse(""))
        self.assertIsNone(parse("   ...  "))

    def test_directions(self):
        self.assertEqual(parse("n"), Command("go", "north"))
        self.assertEqual(parse("go n"), Command("go", "north"))
        self.assertEqual(parse("Go North!"), Command("go", "north"))
        self.assertEqual(parse("enter"), Command("go", "in"))

    def test_abbreviations(self):
        self.assertEqual(parse("i"), Command("inventory"))
        self.assertEqual(parse("x lamp"), Command("examine", "lamp"))
        self.assertEqual(parse("l"), Command("look"))

    def test_articles_stripped(self):
        self.assertEqual(parse("take the brass key"), Command("take", "brass key"))
        self.assertEqual(parse("take a box of matches"), Command("take", "box of matches"))

    def test_verb_phrases(self):
        self.assertEqual(parse("pick up the key"), Command("take", "key"))
        self.assertEqual(parse("look at note"), Command("examine", "note"))

    def test_prepositions(self):
        self.assertEqual(
            parse("unlock the door with the brass key"),
            Command("unlock", "door", "with", "brass key"),
        )
        self.assertEqual(parse("put gem in box"), Command("put", "gem", "in", "box"))
        self.assertEqual(parse("light lamp with"), Command("light", "lamp", "with", None))


if __name__ == "__main__":
    unittest.main()
