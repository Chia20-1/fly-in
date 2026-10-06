# Fly-in: 14-day project plan

**Start:** 6 October 2026  
**Evaluation:** 19 October 2026 — day 14  
**Scope:** Mandatory requirements from `fly-in.pdf`, version 2.0  
**Estimated time:** 4–6 focused hours per day

Finish implementation by day 11. Use days 12 and 13 for validation,
documentation, and evaluation practice.

## Scope and priorities

Build an object-oriented Python program that reads a map, routes every drone
from start to end, respects all movement rules, and displays the simulation.

- Use Python 3.10 or later.
- Implement graph algorithms yourself; do not use graph helper libraries.
- Use colored terminal output for the mandatory visual representation.
- Include type hints and PEP 257 docstrings. Pass flake8 and mypy.
- Provide the required Makefile and English README.
- Skip the GUI, optional `lint-strict` target, and Challenger Map.

Work in this order: **valid input → legal movements → complete simulation →
multiple routes → better turn counts → evaluation preparation**.

## Daily routine

1. Read the day's checklist and choose the first unfinished task.
2. Implement a small piece you can explain.
3. Run a small map that exercises that behavior.
4. Run lint and fix new errors.
5. Record remaining issues and commit the day's working progress.

Use small development tests to check tricky behavior. The brief describes tests
as development aids that are not submitted or graded.

## Day 1 — Tuesday, 6 October: Set up the project

- [ ] Read the mandatory, constraints, README, and submission sections.
- [ ] Create a Python virtual environment and install flake8 and mypy.
- [ ] Add `.gitignore` entries for the environment and Python/tool caches.
- [ ] Sketch the responsibilities of `Zone`, `Connection`, `Graph`, `Drone`,
      `MapParser`, `Router`, `Simulation`, and `TerminalRenderer`.
- [ ] Create root-level Python files and an entry point that accepts a map path.
- [ ] Add Makefile targets: `install`, `run`, `debug`, `clean`, and `lint`.
- [ ] Start `README.md` with the required curriculum line and your login.

**Done when:** The entry point runs, the Makefile targets are usable, and you
can explain which class owns each responsibility.

## Day 2 — Wednesday, 7 October: Parse valid maps

- [ ] Read input files with a context manager and keep source line numbers.
- [ ] Parse `nb_drones`, `start_hub`, `end_hub`, and regular `hub` lines.
- [ ] Parse integer coordinates and metadata in any order.
- [ ] Apply defaults: normal zone, no color, zone capacity 1, link capacity 1.
- [ ] Parse bidirectional connections between previously defined zones.
- [ ] Ignore comments beginning with `#`.
- [ ] Load the example from the brief and inspect the resulting graph.

**Done when:** A valid map produces the correct typed objects and adjacency
information, including metadata and defaults.

## Day 3 — Thursday, 8 October: Reject invalid input clearly

- [ ] Require a positive drone count in the first required input line.
- [ ] Require exactly one start and exactly one end.
- [ ] Reject duplicate zone names, invalid coordinates, and names containing
      spaces or dashes.
- [ ] Reject invalid zone types and malformed metadata blocks.
- [ ] Validate capacity values; handle start/end capacity metadata according
      to the brief's unlimited-capacity exception.
- [ ] Reject unknown connection endpoints and duplicate undirected connections,
      including `a-b` followed by `b-a`.
- [ ] Report parsing failures with a line number and a specific cause.
- [ ] Handle missing or unreadable files without an unhandled exception.

**Done when:** Each invalid case stops cleanly with a useful error message.

## Day 4 — Friday, 9 October: Route one drone

- [ ] Implement weighted shortest-path search, such as Dijkstra's algorithm,
      without graph helper libraries.
- [ ] Use the destination zone's cost: normal/priority 1, restricted 2.
- [ ] Exclude blocked zones from usable routes.
- [ ] Prefer priority zones when choosing otherwise equivalent routes.
- [ ] Reconstruct a route from start to end.
- [ ] Detect an unreachable end and report it as an unsolvable map, separately
      from a parsing error.
- [ ] Check a normal route, a restricted route, a blocked shortcut, and a
      disconnected graph.

**Done when:** Route costs are correct and unreachable maps terminate clearly.

## Day 5 — Saturday, 10 October: Simulate simultaneous normal moves

- [ ] Give drones unique IDs and track their current positions.
- [ ] Plan the entire turn before applying any state changes.
- [ ] Support moving, waiting, and delivery at the end zone.
- [ ] Treat start and end as having unlimited occupancy.
- [ ] Allow a drone to enter a space another drone vacates in the same turn.
- [ ] Remove delivered drones from active tracking.
- [ ] Stop when all drones are delivered.

**Check:** On `start → A → B → end`, with capacity 1 and two drones, both
drones finish in four turns. On turn 2, the first moves to B while the second
moves to A.

**Done when:** A column of drones advances together without sequential-update
artifacts.

## Day 6 — Sunday, 11 October: Enforce capacities

- [ ] Calculate zone occupancy after planned departures and arrivals.
- [ ] Enforce `max_drones` on regular zones.
- [ ] Enforce `max_link_capacity` on each shared bidirectional connection.
- [ ] Resolve competing movement proposals before committing the turn.
- [ ] Use a deterministic choice when drones compete for the same space.
- [ ] Check default capacities, capacities greater than 1, and competing routes.

**Done when:** Every committed turn respects both zone and connection limits.

## Day 7 — Monday, 12 October: Handle restricted transit

- [ ] Represent a drone in transit on a connection explicitly.
- [ ] Reserve destination capacity before starting a restricted movement.
- [ ] Make the drone arrive on the following turn; never let it wait in transit.
- [ ] Count the occupied connection while the drone is in transit.
- [ ] Allow another drone to start crossing on the turn the previous drone
      arrives and frees the connection.
- [ ] Check arrival conflicts when multiple connections lead to one zone.

**Check:** Reproduce the brief's sequence:

```text
D1-restrictedConn
D1-restrictedZone D2-restrictedConn
D2-restrictedZone
```

**Done when:** Every restricted movement takes exactly two turns and every
scheduled arrival has room.

## Day 8 — Tuesday, 13 October: Complete a safe baseline

- [ ] Connect parsing, routing, simulation, and movement output end to end.
- [ ] Complete each supplied mandatory map with a safe route and waiting.
- [ ] Check that all drones arrive and no capacity rule is violated.
- [ ] Detect a state with unfinished drones and no possible progress; report
      the problem rather than looping indefinitely.
- [ ] Identify alternate routes for the multiple-path scheduler.

**Done when:** The baseline completes all supplied mandatory maps legally.

## Day 9 — Wednesday, 14 October: Distribute drones across routes

- [ ] Compare route travel times and available capacity.
- [ ] Assign drones to alternate routes when this improves predicted arrival.
- [ ] Account for shared zones and links when routes overlap.
- [ ] Add strategic waiting where immediate movement would block later progress.
- [ ] Cache reusable route information where appropriate.
- [ ] Check forks, merging paths, loops, dead ends, and bottlenecks.

**Done when:** The scheduler uses multiple routes where useful and completes
the checked maps without conflicts or deadlocks.

## Day 10 — Thursday, 15 October: Finish output and visualization

- [ ] Print one movement line per simulation turn.
- [ ] Use space-separated `D<ID>-<zone>` tokens for arrivals at zones.
- [ ] Use `D<ID>-<connection>` tokens while entering restricted transit.
- [ ] Omit stationary drones and stop tracking delivered drones.
- [ ] Show movements and zone states using colored terminal feedback.
- [ ] Handle arbitrary valid single-word color values gracefully.
- [ ] Provide an uncolored movement-output mode for verification; keep extra
      visual state information separate from the required movement lines.

**Done when:** Output follows the specified format and the terminal display
makes drone movement and occupancy understandable.

## Day 11 — Friday, 16 October: Validate and improve performance

- [ ] Run all nine supplied mandatory benchmark maps.
- [ ] Check movement legality and capacity compliance on every run.
- [ ] Record turn counts in the table below.
- [ ] Fix correctness defects before improving throughput.
- [ ] Reduce avoidable waiting and improve route allocation where time permits.
- [ ] Freeze mandatory features at the end of the day.

| Supplied map | Reference optimum | Your turns | Valid run? |
|---|---:|---:|---|
| Linear path, 2 drones | 4 | | |
| Simple fork, 4 drones | 4 | | |
| Basic capacity, 4 drones | 4 | | |
| Dead end trap, 5 drones | 8 | | |
| Circular loop, 6 drones | 10 | | |
| Priority puzzle, 5 drones | 6 | | |
| Maze nightmare, 8 drones | 13 | | |
| Capacity hell, 12 drones | 16 | | |
| Ultimate challenge, 15 drones | 26 | | |

**Done when:** Every mandatory feature works and every supplied mandatory map
finishes legally.

The brief says correctness is independent of turn count, but later mentions
points for staying within 25% of optimum and for reaching optimum. Record the
results and prioritize correctness before optimization.

## Day 12 — Saturday, 17 October: Complete quality checks and README

- [ ] Check unfamiliar maps: disconnected graph, blocked-only route, direct
      start-to-end link, restricted bottleneck, and shared-route capacities.
- [ ] Repeat malformed-input and file-error checks.
- [ ] Run `make lint` and fix every error.
- [ ] Review type hints, docstrings, resource handling, and exception handling.
- [ ] Complete the English README checklist below.
- [ ] Verify that documented commands and example output actually work.

The mandatory lint target must run:

```sh
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
```

README checklist:

- [ ] First line: `*This project has been created as part of the 42 curriculum by <login1>[, <login2>[, <login3>[...]]].*`
      Replace placeholders and optional notation with the actual author logins.
- [ ] Description: project purpose and overview.
- [ ] Instructions: installation, execution, and relevant commands.
- [ ] Resources: references and an accurate explanation of AI-assisted tasks
      and affected parts of the project.
- [ ] Detailed algorithm choices and implementation strategy.
- [ ] Visual representation features and how they help the user.
- [ ] Example input and verified expected output.

**Done when:** Lint passes and someone unfamiliar with the project can run it
using only the README.

## Day 13 — Sunday, 18 October: Rehearse evaluation

- [ ] Perform a fresh environment setup from the README.
- [ ] Check `install`, `run`, `debug`, `clean`, and `lint`.
- [ ] Ask a peer to try valid, invalid, and unfamiliar maps.
- [ ] Explain the parser, route selection, waiting, and simultaneous updates.
- [ ] Explain restricted destination reservations and connection reuse.
- [ ] Explain algorithm complexity, caching, and memory usage.
- [ ] Practise a small modification, such as changing a display detail.
- [ ] Fix remaining defects and rerun the affected checks.
- [ ] Confirm required deliverables are inside the Git repository and follow
      the brief's instruction to place files at its root.
- [ ] Review Git status and commit the evaluation-ready version.

**Done when:** You can demonstrate the project and explain its behavior without
relying on generated explanations.

## Day 14 — Monday, 19 October: Evaluate

- [ ] Run the final lint check.
- [ ] Confirm the evaluated repository contains the completed work.
- [ ] Demonstrate a normal map, restricted transit, multiple routes, and
      capacity handling.
- [ ] Demonstrate a parsing error and an unsolvable map.
- [ ] Show the required movement output and colored visualization.
- [ ] Present benchmark turn counts and explain routing decisions.
- [ ] Be ready to explain or modify a small part of your code.

**Done when:** Mandatory project evaluation is complete.

## If the schedule slips

Reduce optimization time on days 9–11 first. Keep multiple-path support, but
defer fine-tuning exact benchmark optima. Preserve parser validation, legal
movement scheduling, restricted transit, visualization, lint, documentation,
and the day-13 rehearsal.

Do not add bonus work before evaluation.
