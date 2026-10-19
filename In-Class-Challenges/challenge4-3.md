# Challenge 4.3: What's a Class Hierarchy?

## Class Hierarchy Diagram

The following Mermaid diagram illustrates the inheritance
relationships between the Python classes provided in
Challenge 4.3, including multiple inheritance.

```mermaid
classDiagram
    Effect <|-- Poison
    Effect <|-- Regen

    Item <|-- Key
    Item <|-- Weapon
    Weapon <|-- Sword
    Weapon <|-- Bow
    Item <|-- Consumable
    Consumable <|-- Potion

    Describable <|-- Entity
    Entity <|-- Creature
    Creature <|-- Player
    Creature <|-- Monster
    Monster <|-- Goblin
    Flammable <|-- Goblin
    Monster <|-- Skeleton

    class Lockable
```