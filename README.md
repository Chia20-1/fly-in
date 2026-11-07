*This project has been created as part of the curriculum by chilim*

# Description


# Instruction

How to access the map:

```sh
python3 main.py <map_file_path>  # Required positional argument
make run                       # Use the default map
make run MAP=<map_file_path>    # Override the default map
```

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