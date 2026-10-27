```
Router
│
├── __init__(graph)
│   Store the graph.
│
├── Find neighboring zones
│   Read graph.adjacency[current_zone.name].
│   Each connection can be traversed in either direction.
│
├── Determine movement cost
│   Look at the destination zone:
│   normal / priority → 1
│   restricted        → 2
│   blocked           → skip
│
└── find_route()
    Search from start to end.
    Remember the cheapest cost to each zone.
    Remember which zone led to it.
    Reconstruct and return the route.
```

| Step | What you implement | What you should be able to inspect |
|---|---|---|
| 1 | Store the graph in `Router` | Router can access start, end and adjacency |
| 2 | Find neighbors of one zone | Neighboring zone names and their connections |
| 3 | Assign destination movement costs | Normal = 1, restricted = 2; blocked skipped |
| 4 | Track cheapest discovered costs | A dictionary such as `{"start": 0, "A": 1}` |
| 5 | Track predecessors | A dictionary such as `{"A": "start"}` |
| 6 | Reconstruct the route | An ordered list from start to end |
| 7 | Prefer priority zones on equal-cost choices | A consistent tie-breaking rule |

<br>
Notice that the current zone can be either endpoint. You cannot always take connection.to_zone as the neighbor.
Also, endpoints are strings, while drone.current_zone is a Zone object. A lookup will help bridge them:
```
zones_by_name = {zone.name: zone for zone in graph.zones}
```

Conceptual movement:
```
Current Zone object
        ↓ get its name
Adjacency connections
        ↓ choose the opposite endpoint
Neighbor name
        ↓ look it up
Neighbor Zone object
        ↓ inspect its type
Movement cost
```