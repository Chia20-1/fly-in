from models import Connection, Drone, Graph, Zone
from router import Route, Router

# Each entry: arrival turn, destination, connection used
Plan = list[tuple[int, Zone, Connection]]
Movement = tuple[int, str]
Turn = list[Movement]
SimulationOutput = list[Turn]


class Scheduler:
    """
    """
    def __init__(self, graph: Graph) -> None:
        """
        """
        self.graph: Graph = graph
        self.output: SimulationOutput = []
        self.zone_use: dict[tuple[int, Zone], int] = {}
        self.link_use: dict[tuple[int, Connection], int] = {}

    def _make_plan(self, route: Route, delay: int) -> Plan:
        """
        """
        turn = delay
        plan: Plan = []

        for destination, connection in route:
            if destination.zone == "blocked":
                raise ValueError("A route cannot enter a blocked zone")

            turn += 2 if destination.zone == "restricted" else 1
            plan.append((turn, destination, connection))
        return plan

    def _has_capacity_for_plan(self, plan: Plan) -> bool:
        """
        """
        for arrival, destination, connection in plan:
            crossing = arrival
            if destination.zone == "restricted":
                crossing = arrival - 1

            has_unlimited_zone_capacity = (
                destination is self.graph.start_hub
                or destination is self.graph.end_hub
            )

            if not has_unlimited_zone_capacity:
                occupied = self.zone_use.get((arrival, destination), 0)
                if occupied >= destination.max_drones:
                    return False

            used = self.link_use.get((crossing, connection), 0)
            if used >= connection.max_link_capacity:
                return False

        return True

    def schedule_drone(self, drone: Drone, route: Route) -> None:
        """
        """
        departure_delay = 0
        plan = self._make_plan(route, departure_delay)

        while not self._has_capacity_for_plan(plan):
            departure_delay += 1
            plan = self._make_plan(route, departure_delay)

        for arrival_turn, destination, connection in plan:
            crossing_turn = arrival_turn

            if destination.zone == "restricted":
                crossing_turn = arrival_turn - 1

            # Reserve zone capacity for arrival turn
            zone_key = (arrival_turn, destination)
            self.zone_use[zone_key] = self.zone_use.get(zone_key, 0) + 1

            # Reserve connection capacity on the crossing turn
            link_key = (crossing_turn, connection)
            self.link_use[link_key] = self.link_use.get(link_key, 0) + 1

            # Create output entries up to the arrival turn
            while len(self.output) < arrival_turn:
                self.output.append([])

            if destination.zone == "restricted":
                connection_name = (
                    f"{connection.from_zone}-{connection.to_zone}"
                )
                self.output[crossing_turn - 1].append(
                    (drone.id, connection_name)
                )

            self.output[arrival_turn - 1].append(
                (drone.id, destination.name)
            )


class Simulation:
    """
    """
    def __init__(self, graph: Graph, router: Router) -> None:
        """
        """
        self.graph = graph
        self.router = router
        self._drones_by_id: dict[int, Drone] = {
            drone.id: drone for drone in graph.drones
        }
        self.occupancy: dict[Zone, int] = {}
        self.in_transit: dict[int, str] = {}
        self.output: SimulationOutput = []

    def _init_simulation(self) -> None:
        """
        """
        self.output = []
        self.in_transit.clear()

        for drone in self.graph.drones:
            drone.current_zone = self.graph.start_hub

        self._update_occupancy()

    def _build_schedule(self) -> SimulationOutput:
        """
        """
        scheduler = Scheduler(self.graph)
        route = self.router.get_best_route(self.graph.end_hub.name)

        for drone in self.graph.drones:
            scheduler.schedule_drone(drone, route)

        return scheduler.output

    def _apply_turn(self, turn: Turn) -> None:
        """
        """
        for drone_id, location in turn:
            drone = self._drones_by_id[drone_id]
            destination = self.graph.zone_lookup.get(location)

            if destination is None:
                self.in_transit[drone_id] = location
            else:
                drone.current_zone = destination
                self.in_transit.pop(drone_id, None)

        self._update_occupancy()

    def _update_occupancy(self) -> None:
        """
        """
        self.occupancy = {
            zone: 0 for zone in self.graph.zones
        }

        for drone in self.graph.drones:
            if drone.id not in self.in_transit:
                self.occupancy[drone.current_zone] += 1

    def run_simulation(self) -> tuple[SimulationOutput, int]:
        """
        """
        self._init_simulation()
        self.output = self._build_schedule()

        for turn in self.output:
            self._apply_turn(turn)

        return self.output, len(self.output)
