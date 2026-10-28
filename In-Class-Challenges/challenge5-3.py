# In-Class Challenge 5.3: Fix Overly-Complex Class

# Handles the player's character stats
class Stats:
    def __init__(self):
        self.str = 9
        self.dex = 12
        self.con = 8
        self.int = 18
        self.wis = 10
        self.cha = 2

class Armor:
    def __init__(self):
        self.items = [
            {"name": "iron helmet", "ac": 8},
            {"name": "chain mail", "ac": 16}
        ]


class Weapon:
    def __init__(self, name, damage):
        self.name = name
        self.damage = damage


class Player:
    def __init__(self, name):
        self.name = name
        self.hp = 10
        self.stats = Stats()
        self.armor = Armor()
        self.weapon = Weapon("short sword", "1d6")

    def damage(self, points):
        self.hp -= points

    def compute_damage(self, base):
        pass


p = Player("Alfredo")

print(p.name)
print(p.hp)
print(p.stats.str)
print(p.armor.items)
print(p.weapon.name)

p.damage(3)
print(p.hp)
