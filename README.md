*This project has been created as part of the curriculum by chilim*

# Description


# Instruction


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

# 
