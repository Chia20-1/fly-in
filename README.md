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

## Project structure

```text
fly-in/
|-- .gitignore
|-- Makefile
|-- README.md
|-- main.py            # Command-line arguments and program orchestration
|-- map_parser.py      # Map syntax, declaration order, and source line numbers
|-- map_config.py      # Pydantic models and numeric field validation
|-- map_validation.py  # Zone uniqueness and connection consistency
|-- models.py          # Drone, Zone, Connection, and Graph classes
|-- router.py          # Dijkstra-based route finding
|-- simulation.py      # Route scheduling and turn-by-turn state updates
|-- text_output.py     # Terminal movement output
|-- renderer.py        # Interactive Pygame visualization
|-- error.py           # Custom parsing and map-validation exceptions
|-- maps/              # Easy, medium, hard, and challenger maps
```

## Execution flow

`main.py` coordinates the following stages:

```text
Command-line arguments
        |
        v
MapParser.parse()
    Read declarations and check syntax and required counts.
    Parse zones and connections in source-line order.
    Require connection endpoints to be declared first.
    Preserve source line numbers for error reporting.
        |
        v
MapConfig.model_validate()
    Validate integer inputs, zone types, and positive capacities.
    Convert numeric strings and apply default values.
        |
        v
MapValidation.validate()
    Reject duplicate zone names, unknown connection endpoints,
    and duplicate bidirectional connections.
        |
        v
Graph
    Create zones, connections, and drones at the starting hub.
    Build zone and adjacency lookup tables.
        |
        v
Simulation.run_simulation()
    Router: find the best route and candidate alternatives.
    Scheduler: reserve zone and connection capacity for each drone.
    Simulation: apply the resulting schedule one turn at a time.
        |
        v
SimulationOutput
    Movement records grouped by turn.
        |
        +-- Default ------> TextOutput.print_output()
        |                   Print one movement line per turn.
        |
        +-- --visual -----> Renderer.run()
                            Replay turns with Previous/Next controls.
```

The simulation finishes before either output mode begins. The renderer replays
its movement records rather than recalculating routes or running a second
simulation.

Parsing, configuration, and consistency errors are reported to standard error
before simulation begins. Source line numbers are included where available.
An unreachable destination is reported as a routing error, and Pygame runtime
errors are handled in visualization mode. Failed execution exits with a nonzero
status.

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