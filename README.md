*This project has been created as part of the curriculum by chilim*

# Description


# Instructions 

### Requirements

- Python 3.10 or later
- `make`
- A graphical desktop environment for visualization mode

### Install dependencies

From the project root, run:
```sh
make install
```

This creates a virtual environment at `.venv/` and installs the runtime
dependencies (`pydantic` and `pygame`) and development tools (`flake8`
and `mypy`).

### Run in text mode

Run the default map in text mode:

```sh
make run
```

Run a specific map in text mode:

```sh
make run MAP=maps/hard/03_ultimate_challenge.txt
```

### Run in visualization mode

Open the default map in a Pygame window:

```sh
make visual
```

Open a specific map in a Pygame window:
```sh
make visual MAP=maps/medium/02_circular_loop.txt
```

### Run via the Python entry point

```
.venv/bin/python main.py <map_file_path> [--visual]
```

- `<map_file_path>`: required path to a map file.
- `--visual`: optional flag that enables graphical visualization.
  Place it after the map path.

Paths are relative to the current working directory unless an absolute path
is supplied. Errors are printed to standard error, and the program exits
with a nonzero status when execution fails.

### Development commands

Run linter-standard check and type annotation check:
```sh
make lint
```

Run stricter code-style and type check:
```sh
make lint-strict
```

Run the program using Python's debugger:
```sh
make debug MAP=maps/easy/01_linear_path.txt
```

Remove generated caches only:
```sh
make clean
```

Remove generated caches and the virtual environment:
```sh
make fclean
```

> After `make fclean`, run `make install` before executing the program again.
 

# Architecture
```
root/
|-- .gitignore
|-- Makefile
|-- README.md
|-- modules
	|-- connection.py
	|-- drone.py
	|-- graph.py
	|-- zone.py
|-- main.py
|-- parser.py
|-- renderer.py
|-- simulation.py
```
*Project's Folder & File Structure*
```
main.py
   |
   v
MapParser
   |
   |-- 1. Read file
   |-- 2. Parse lines into raw dictionaries
   |-- 3. Check syntax (missing :, unknown key)
   |-- 4. Check structural completeness:
   |       - Exactly one start_hub?
   |       - Exactly one end_hub?
   |       - Required hubs/connections present?
   |
   |-- ERROR? --> Raise MapParserError
   |                  |
   |                  v
   |              main.py catches error
   |              Exit program
   |
   v
Pydantic
   |
   |-- Convert values to types
   |-- Validate field constraints
   |-- Apply default values
   |
   v
Build simulation graph
```

# Map Config
| Entity | Attributes |
| --- | --- |
| Zone | x-coordinate, y-coordinate, type: [hub, start_hub, end_hub], [metadata] |
| Connection | type: [normal, blocked, restricted, priority], current drone, from_zone, to_zone |
| Graph | zone, Connection, Start Hub, End Hub |
| Drone | id, state |

# Algorithm

## Algorithm Choice

## Implementation Strategy

# Visual Representation

┌──────────────────────────────┐
│ Turn counter / controls      │ 80 pixels
├──────────────────────────────┤
│                              │
│ Map, with 60 pixels padding  │ 620 pixels
│ around its edges             │
│                              │
├──────────────────────────────┤
│ Status / legend              │ 100 pixels
└──────────────────────────────┘
          1200 pixels

```Python
self.width = 1200
self.height = 800
self.margin = 60
self.radius = 14

self.header_height = 80
self.footer_height = 100
```

# Resources
- **Dijkstra Algorithm:** Hand-drawn practice for finding the shortest path across vertices — [YouTube](https://www.youtube.com/watch?v=eFZCPlZCyIM)
- **Dijkstra Alrgorithm:** Concept explaination and understanding — [Youtube](https://www.youtube.com/watch?v=bZkzH5x0SKU)
- **pygame official** - [pygame.org](https://www.pygame.org/docs/tut/newbieguide.html)
- **pygame introduction** - [GeeksforGeeks](https://www.geeksforgeeks.org/python/pygame-tutorial/)