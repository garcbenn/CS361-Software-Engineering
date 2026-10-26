# In-Class Challenge 5.1: Define an Interface

## On-Car Computer

The on-car computer handles the buttons, floor display, bell, doors, position sensor, and communication with the lift motor computer.

### Inputs

```python
def handle_button_press(button: int) -> None
def get_current_floor() -> int
def get_door_status() -> bool
def get_motor_status() -> str
```

### Outputs

```python
def display_floor(floor: int) -> None
def open_door() -> bool
def close_door() -> bool
def ring_bell() -> None
def request_floor(floor: int) -> bool
```

## Lift Motor Computer

The lift motor computer receives commands from the on-car computer and controls the elevator's movement.

### Inputs

```python
def move_up() -> bool
def move_down() -> bool
def stop_motor() -> bool
```

### Outputs

```python
def get_motor_status() -> str
def get_motor_direction() -> str
```

## Return Values

- `bool`: Returns `True` if a command was accepted and `False` if it failed.
- `int`: Returns a floor number.
- `str`: Returns information such as `"UP"`, `"DOWN"`, `"STOPPED"`, or `"ERROR"`.
- `None`: The function does not return a value.

## Questions and Assumptions

1. I assume the elevator doors must be closed before the motor can move.
2. I assume the on-car computer sends movement requests to the lift motor computer.
3. How many floors does the elevator support?
4. Does the lift motor computer automatically stop at the requested floor, or does the on-car computer tell it when to stop?
5. Is there an emergency stop button, and which computer would handle it?