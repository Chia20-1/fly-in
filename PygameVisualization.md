# Simple Pygame visualization for Fly-in

Use your existing simulation output as the playback data. Run the simulation
once, then let Pygame display whichever turn the user selects.

You need the graph for map coordinates and connections, and the output for
drone movements. Reuse the existing `graph.zone_lookup`.

This guide proposes a small extension to your current `Renderer`. The Python
files have not been changed.

## 1. The basic structure

```text
main.py
  -> build graph and router
  -> simulation.run_simulation()
       returns output, turns
  -> TextOutput(output, turns).print_output()
  -> Renderer(graph, output).run()       proposed addition
```

The renderer needs these playback attributes:

| Attribute | What it contains |
| --- | --- |
| `self.graph` | Your existing graph |
| `self.output` | The output returned by the simulation |
| `self.current_turn` | The selected turn, starting at 0 |
| `self.positions` | Each drone's logical location at the selected turn |

It also needs the usual Pygame screen, clock, font, and two button rectangles.
Keep your existing window dimensions.

You do not need a history of snapshots or a new connection lookup table.
`self.positions` is just the current display state, rebuilt from the output
when the selected turn changes.

## 2. What your output means

Your `simulation.py` defines:

```python
Movement = tuple[int, str]
Turn = list[Movement]
SimulationOutput = list[Turn]
```

A small example for the linear map, assuming drone IDs 1 and 2:

```python
output = [
    [(1, "waypoint1")],
    [(1, "waypoint2"), (2, "waypoint1")],
    [(1, "goal"), (2, "waypoint2")],
    [(2, "goal")],
]
```

Each list contains only the drones that moved during that turn.

Drone 2 is missing from the first list because it waits at start. Drone 1 is
missing from the last list because it stays at goal.

**A drone missing from a turn keeps its previous location.**

An empty list still counts as one simulation turn. Apply all movements in a
turn before drawing, so they appear together.

## 3. Keep the turn numbering clear

| Selected turn | What to display |
| --- | --- |
| 0 | All drones at start |
| 1 | Positions after applying `output[0]` |
| 2 | Positions after applying `output[0]` and `output[1]` |
| `len(output)` | Final positions |

To display turn `t`, apply the movements in `output[:t]`.

At turn 0, that slice is empty, so every drone remains at start.

Your simulation already applies every turn before returning. Therefore,
`drone.current_zone` contains the final simulated position. Build the viewer's
initial positions from `graph.start_hub.name`, rather than from
`drone.current_zone`.

Use the actual `drone.id` values from `graph.drones`.

## 4. Rebuild positions from the output

Use one method, proposed as `_update_positions(self)`.

Its job is:

```text
Start self.positions with every drone at the start hub.

For each turn in output[:current_turn]:
    For each (drone_id, location) in that turn:
        Replace that drone's location in self.positions.
```

The initial dictionary can use the data you already have:

```python
self.positions = {
    drone.id: self.graph.start_hub.name
    for drone in self.graph.drones
}
```

Store location strings, such as `"waypoint1"` or `"loop_b-exit_point"`.
Convert them to drawing coordinates when rendering.

For the example above:

| Turn | Drone 1 | Drone 2 |
| --- | --- | --- |
| 0 | start | start |
| 1 | waypoint1 | start |
| 2 | waypoint2 | waypoint1 |
| 3 | goal | waypoint2 |
| 4 | goal | goal |

### Why Previous works

Suppose you are viewing turn 3 and press Previous:

1. Change the selected turn to 2.
2. Reset the displayed positions to start.
3. Apply `output[:2]`.
4. Draw the resulting positions.

You do not need to reverse any movements or save earlier dictionaries.
Next uses exactly the same process with a larger selected turn.

Rebuilding repeats some work when navigating, but keeps the first version
simple. Do it when the selected turn changes, rather than on every drawing frame.
You can consider caching later if playback actually becomes slow.

## 5. A small set of renderer methods

Keep the methods focused:

| Method | Responsibility |
| --- | --- |
| `__init__(self, graph, output)` | Store the data, select turn 0, and build initial positions |
| `start(self)` | Set up Pygame, the screen, clock, font, layout, and buttons |
| `configure_layout(self)` | Calculate the map scale and offsets |
| `to_screen(self, x, y)` | Convert map coordinates to screen pixels |
| `_update_positions(self)` | Rebuild the selected turn's drone locations from output |
| `set_turn(self, turn)` | Accept a valid turn number and rebuild positions |
| `draw(self)` | Draw the map, current drone positions, and controls |
| `run(self)` | Start the window and repeat event handling and drawing |

For `set_turn()`, accept turn numbers from 0 through `len(self.output)`,
inclusive. Ignore requests outside that range.

Both buttons use this method:

```text
Next     -> set_turn(current_turn + 1)
Previous -> set_turn(current_turn - 1)
```

You can handle events directly inside `run()` initially. Extract more drawing
or event methods only when those sections become difficult to read.

## 6. How the functions call each other

```text
Renderer(graph, output)
  -> store graph and output
  -> current_turn = 0
  -> _update_positions()

renderer.run()
  -> start()                       once
       -> initialize Pygame
       -> create screen, clock, font, and buttons
       -> configure_layout()

  -> while window is running:
       -> read events
            -> Next click: set_turn(current_turn + 1)
            -> Previous click: set_turn(current_turn - 1)
                 -> _update_positions()
            -> window close: stop loop

       -> if closing, leave loop
       -> draw()
            -> draw connections and zones using to_screen()
            -> draw drones using self.positions and to_screen()
            -> draw buttons and turn label
       -> pygame.display.flip()
       -> clock.tick(60)

  -> pygame.quit()
```

Move the `pygame.init()` currently in your constructor into `start()` for
this structure, so setup happens in one place.

A button click changes the selected turn. It does not rerun the simulation,
router, or scheduler.

## 7. Draw the map using the graph you already have

For each item in `graph.connections`:

1. Get its endpoints using `graph.zone_lookup[connection.from_zone]` and
   `graph.zone_lookup[connection.to_zone]`.
2. Convert their coordinates using `to_screen()`.
3. Draw a line between them.

For each zone in `graph.zones`:

1. Convert `zone.x` and `zone.y` using `to_screen()`.
2. Draw a circle and the zone's name.

Draw connections first, so zone circles appear above the lines.

Your existing dimensions leave this map area:

```text
Window:             1200 x 800
Header:             80 pixels
Footer:             100 pixels
Margin:             60 pixels

Map left:           60
Map top:            140
Available width:    1080
Available height:   500
```

In `configure_layout()`, find the smallest and largest x and y coordinates.
Calculate one scale that fits both coordinate spans into the available area,
then center the result.

For each nonzero span, calculate available pixels divided by that span. Use
the smaller ratio as the scale. Ignore zero spans; if both are zero, use scale 1.

With `span_x = max_x - min_x` and `span_y = max_y - min_y`:

```text
offset_x = 60 + (1080 - span_x * scale) / 2
offset_y = 140 + (500 - span_y * scale) / 2

screen_x = offset_x + (x - min_x) * scale
screen_y = offset_y + (max_y - y) * scale
```

Round screen coordinates to integers. This version displays increasing map y
upward, while Pygame's pixel y increases downward.

Your linear map has zero y span. Do not divide by that span. With this layout,
its four zones appear at x = 60, 420, 780, and 1140, all at y = 390.

## 8. Draw each drone at its logical location

Loop through `self.positions.items()`. Each item gives you a drone ID and
a location string.

### Location is a zone name

For `"waypoint1"`:

1. Get `zone = self.graph.zone_lookup[location]`.
2. Convert `zone.x, zone.y` to pixels.
3. Draw a small drone marker and its ID there.

### Location is a connection name

Your scheduler uses a token such as `"loop_b-exit_point"` for restricted transit.

Your map format forbids dashes in zone names, so you can split that token into
the two endpoint names and resolve both using the existing `graph.zone_lookup`.

Draw the drone at the midpoint of the two screen positions:

```text
drone_x = (endpoint1_x + endpoint2_x) / 2
drone_y = (endpoint1_y + endpoint2_y) / 2
```

Check whether the location is in `graph.zone_lookup` first; otherwise handle
the connection token produced by your scheduler.

The token's endpoint order does not necessarily indicate travel direction,
but direction does not matter for drawing a midpoint.

On the next recorded turn, the output moves the drone to the restricted zone,
so the same position-building process handles its arrival.

For several drones at the same location, begin with a count or a combined
label such as `D1, D2`. You can add separate marker offsets later.

## 9. Implement Next and Previous buttons

A simple button is a rectangle, a label, and a click check.

Possible rectangles inside your footer:

```python
self.previous_button = pygame.Rect(380, 725, 160, 45)
self.next_button = pygame.Rect(660, 725, 160, 45)
```

Draw the rectangles using `pygame.draw.rect()`. Render the labels with a
font and place them using `screen.blit()`.

When handling events:

```text
If event is MOUSEBUTTONDOWN and event.button is 1:
    If previous_button.collidepoint(event.pos):
        request current_turn - 1
    Else if next_button.collidepoint(event.pos):
        request current_turn + 1
```

Use button-down events so each click requests one step. Checking whether the
mouse is held down every frame can advance many turns from one press.

At turn 0, draw Previous in gray. At `len(output)`, draw Next in gray.
When output is empty, both are gray. The boundary check in `set_turn()`
must still reject invalid requests; gray styling alone does not disable a button.

Left and Right keyboard events can call the same `set_turn()` method.

Show `Turn current_turn / len(output)` in the header.
If displaying movement text, use `output[current_turn - 1]` only when
`current_turn > 0`. At turn 0, display "Initial state".

## 10. A frame is not a simulation turn

The drawing loop keeps the window responsive. It can redraw the same selected
turn many times.

`clock.tick(60)` limits drawing speed to at most roughly 60 frames per second.
It does not advance the simulation.

For this first version, advance turns only through Next, Previous, or their
keyboard shortcuts. Add automatic playback and smooth movement later.

Every frame should:

1. Read events.
2. Clear the screen.
3. Draw the map, drones, and controls.
4. Present the frame with `pygame.display.flip()`.
5. Limit the frame rate.

The official [Pygame introduction](https://www.pygame.org/docs/) demonstrates
this loop. The [Rect reference](https://www.pygame.org/docs/ref/rect.html)
covers button hit testing.

## 11. Small changes your current skeleton needs

| Current code | Change to make |
| --- | --- |
| `Renderer(output, turns)` | Pass `graph` and `output`; derive the turn count from `len(output)` |
| Constructor arguments are not saved | Store `self.graph` and `self.output` |
| `self.pygame.display.set_caption(...)` | Use the imported module: `pygame.display.set_caption(...)` |
| `configure_layout()` has no `self` | Add `self` because it is called on a renderer instance |
| `to_screen()` has no arguments | Give it `self, x, y` |
| `draw(self, output, turns)` | Use `draw(self)` and read the stored data |
| `main.py` imports only `TextOutput` | Also import `Renderer`, then construct it and call `run()` |

Passing `graph` is necessary because output strings contain no map geometry.
The existing graph already supplies the lookup you need.

## 12. Suggested next steps for the current renderer

The design in `renderer.py` is a workable foundation. Complete it incrementally:

1. **Finish layout scaling and coordinate conversion.** Complete
   `_configure_layout()` and give `_to_screen()` the signature
   `_to_screen(self, x: float, y: float) -> tuple[int, int]`. Use one shared
   scale, ignore zero spans, and center the graph in the available area.
   The current renderer's docstring specifies increasing y downward; use that
   convention consistently, or deliberately choose the upward-y alternative
   illustrated in section 7.
2. **Draw a static graph.** Draw connections first, then zones and labels.
   Make `_draw(self)` read the existing renderer state instead of accepting
   duplicate `output` and `turns` arguments. In `_start()`, create the window
   using `(self.width, self.height)` rather than hard-coded dimensions.
   Add an event loop in `run()` that handles window closing, draws the frame,
   calls `pygame.display.flip()`, and limits the frame rate. Ensure
   `pygame.quit()` runs through a `try/finally` around the window lifecycle.
3. **Add forward and backward turn controls.** Route button clicks and
   keyboard shortcuts through the existing `_set_turn()`. Verify that turn 0
   is the initial state and turn `len(self.output)` is the final state.
4. **Draw drones at their recorded locations.** Check for zone names first;
   otherwise resolve the scheduler's connection token and draw the drone at
   the connection midpoint. A connection-label lookup built from
   `graph.connections` is an alternative to splitting tokens and avoids
   depending on the zone-name restriction. Show a count or combined label
   when several drones share a location so they do not hide one another.
5. **Add autoplay or smooth movement only after manual stepping works.**
   Frame rate and simulation turns should remain separate concepts.

When ready to test the viewer, import `Renderer` in `main.py` and call
`Renderer(graph, output).run()` after producing the simulation output.

First layout exercise: if `span_x == 0` but `span_y > 0`, which span should
determine the scale? Confirm the vertical graph stays centered without
dividing by zero.

Check the linear map first. Confirm a waiting drone stays at start and a
delivered drone stays at goal. Then use
`maps/medium/02_circular_loop.txt` to check restricted transit.

Try Next -> Previous -> Next: the final displayed state should be identical.
Also check that neither button can select a turn outside the valid range.

First exercise: at turn 2 in the example output, where should each drone be?
Explain why drawing only the entries in `output[1]` would fail for a turn
where one drone waits.
