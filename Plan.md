**Checks:** Capacity 1, larger capacities, merging paths, competing link usage.

**Done when:** Every committed turn respects zone and link limits.

# Fly-in — Completed Code Structure

Keep application files at the repository root, following the project plan.

```text
fly-in/
├── main.py              # CLI arguments and application orchestration
├── error.py             # Parsing, validation, routing, simulation errors
│
├── map_parser.py        # Text → raw map data; syntax and line numbers
├── map_config.py        # Pydantic schemas, types, defaults, constraints
├── map_validation.py    # Relationships and map consistency
│
├── models.py            # Zone, Connection, Graph, Drone and runtime state
├── router.py            # Weighted paths and alternative route candidates
├── simulation.py        # Turn planning, capacities, reservations, completion
├── renderer.py          # Movement output and colored terminal display
│
├── requirements.txt     # Runtime and development dependencies
├── Makefile             # install, run, debug, clean, lint
├── .gitignore           # Virtual environments and generated caches
├── README.md            # Installation, usage, architecture and examples
├── Planning.md          # Implementation checklist and benchmark results
└── test_map.txt         # Valid example map
```

## Main Responsibilities

| Component | Owns |
|---|---|
| `MapParser` | Reading files and interpreting map syntax |
| `MapConfig` | Typed values, defaults, and field constraints |
| `MapValidation` | Cross-reference and structural checks |
| `Graph` | Zones, bidirectional connections, and adjacency |
| `Drone` | Identity, position, transit state, and delivery status |
| `Router` | Route costs, path reconstruction, and route candidates |
| `Simulation` | Decisions about which drones move each turn |
| `TerminalRenderer` | Formatting committed movements and displaying state |

## Application Flow

```text
Read arguments
    ↓
Parse and validate map
    ↓
Build graph
    ↓
Find usable routes
    ↓
Repeat: plan turn → resolve conflicts → commit turn → render
    ↓
Finish when every drone is delivered
```

### Day 5 — Implement Restricted Transit

- [ ] Represent drones in transit explicitly.
- [ ] Make restricted movement take exactly two turns.
- [ ] Reserve destination capacity before transit begins.
- [ ] Count link occupancy during transit.
- [ ] Process scheduled arrivals without allowing drones to wait in transit.
- [ ] Allow link reuse on the turn a previous crossing finishes.

**Checks:** Consecutive crossings, multiple incoming links, destination reservation conflicts.

**Done when:** Restricted arrivals occur on schedule without capacity violations.

### Day 6 — Complete the First End-to-End Simulation

- [ ] Connect parsing, routing, simulation, and basic movement output.
- [ ] Complete small maps using one safe route and waiting.
- [ ] Detect unfinished simulations with no possible progress.
- [ ] Handle unreachable maps and stalled states clearly.
- [ ] Check that every drone is delivered exactly once.
- [ ] Keep simulation decisions separate from output formatting.

**Done when:** The CLI completes representative maps legally and terminates clearly on failure.

### Day 7 — Support Multiple Routes

- [ ] Generate useful alternative routes.
- [ ] Compare travel time and available capacity.
- [ ] Assign drones across routes when it improves completion time.
- [ ] Account for shared zones and links.
- [ ] Avoid routing decisions that repeatedly block progress.
- [ ] Use deterministic tie-breaking.

**Checks:** Forks, merges, loops, dead ends, and shared bottlenecks.

**Done when:** The scheduler uses multiple routes where useful without conflicts or deadlocks.

### Day 8 — Finish Output and Visualization

- [ ] Print one movement line per simulation turn.
- [ ] Format zone arrivals as `D<ID>-<zone>`.
- [ ] Format restricted transit according to the brief.
- [ ] Omit stationary drones from movement lines.
- [ ] Add colored terminal feedback for movement and occupancy.
- [ ] Handle unknown color names gracefully.
- [ ] Keep visual annotations separate from required movement output.
- [ ] Provide uncolored output for verification.

**Done when:** Output follows the specification and clearly shows simulation progress.

### Day 9 — Validate and Improve

- [ ] Obtain and run all supplied mandatory benchmark maps.
- [ ] Check movement legality throughout each run.
- [ ] Record completion turns.
- [ ] Investigate failures before optimizing.
- [ ] Reduce unnecessary waiting and improve route allocation.
- [ ] Run Flake8 and strict mypy checks.

| Benchmark | Reference optimum* | Your turns | Legal? |
|---|---:|---:|---|
| Linear path | 4 | — | — |
| Simple fork | 4 | — | — |
| Basic capacity | 4 | — | — |
| Dead end trap | 8 | — | — |
| Circular loop | 10 | — | — |
| Priority puzzle | 6 | — | — |
| Maze nightmare | 13 | — | — |
| Capacity hell | 16 | — | — |
| Ultimate challenge | 26 | — | — |

*Values come from the existing project plan; verify them against the original brief.*

**Done when:** Every mandatory map completes legally, with results recorded.

### Day 10 — Documentation and Evaluation Preparation

- [ ] Complete `install`, `run`, `debug`, `clean`, and `lint`.
- [ ] Finish README installation and execution instructions.
- [ ] Explain architecture, routing, scheduling, and restricted transit.
- [ ] Include verified example input and output.
- [ ] Add required resource and AI-assistance disclosures.
- [ ] Verify installation from a fresh environment.
- [ ] Rehearse valid, invalid, unreachable, and restricted maps.
- [ ] Review deliverables and Git status.
- [ ] Commit the completed version.

**Done when:** Another person can install and run the project using the README, and you can explain each major decision.

## 4. Development Routine

For each milestone:

1. Implement one small behavior.
2. Run a map that demonstrates it.
3. Check a relevant failure case.
4. Run lint and type checking.
5. Record remaining issues and commit working progress.

Use development checks that inspect actual positions, capacities, arrivals, and termination—not only exit codes.

## 5. If Time Runs Short

Reduce optimization time first. Preserve:

- Complete input validation.
- Legal simultaneous movement.
- Zone and link capacity enforcement.
- Correct restricted transit.
- Multiple-route support.
- Required output and colored visualization.
- Documentation and evaluation preparation.

Defer GUI work, bonus features, and fine-tuning exact benchmark optima until the mandatory workflow is complete.