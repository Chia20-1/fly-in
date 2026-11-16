from models import Connection, Drone, Graph, Zone
from router import Route, Router

# Each entry: arrival turn, destination, connection used
Plan = list[tuple[int, Zone, Connection]]
Movement = tuple[int, str]
Turn = list[Movement]
SimulationOutput = list[Turn]


class Scheduler:
    """
    Build capacity-aware movement schedules for drones.

    Schedule drones greedily using existing reservations. For each candidate
    route, delay departure until the full plan fits, then select the plan
    with the earliest final arrival. Previously reserved plans are unchanged.

    Attributes:
        graph: Map containing the zones, connections, and endpoint hubs.
        output: Movements grouped by turn. Each movement contains a drone ID
            and a zone name or connection name. Index 0 represents turn 1.
        zone_reservation: Arrival counts keyed by arrival turn and zone.
        link_reservation: Crossing counts keyed by crossing turn
            and connection.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initialize a scheduler with no reservations or movements.

        Args:
            graph: Map whose zones and connections define movement capacities.
        """
        self.graph: Graph = graph
        self.output: SimulationOutput = []
        self.zone_reservation: dict[tuple[int, Zone], int] = {}
        self.link_reservation: dict[tuple[int, Connection], int] = {}

    def _make_plan(self, route: Route, delay: int) -> Plan:
        """
        Build a timed route plan with the given departure delay.

        Entering a restricted zone takes two turns; entering any other
        allowed zone takes one turn. This method does not check or
        reserve capacity.

        Args:
            route: Ordered sequence of destination zones and connections.
            delay: Number of turns to wait before starting the route.

        Returns:
            A list of tuples containing the arrival turn, destination zone,
            and connection used for each step of the route.

        Raises:
            ValueError: If the route enters a blocked zone.
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
        Check whether a plan fits within the existing reservations.

        Check zone capacity on each arrival turn and connection capacity on
        each crossing turn. Start and end hubs have unlimited zone capacity.

        For restricted zones, crossing occurs one turn before arrival.

        This method does not modify reservations.

        Args:
            plan: Timed route plan to check.

        Returns:
            True if every step fits within the available capacity;
            otherwise, False.
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
                occupied = self.zone_reservation.get((arrival, destination), 0)
                if occupied >= destination.max_drones:
                    return False

            used = self.link_reservation.get((crossing, connection), 0)
            if used >= connection.max_link_capacity:
                return False

        return True

    def _find_earliest_plan(self, route: Route) -> Plan:
        """
        Find the earliest feasible plan for a route.

        Start with no departure delay, then increase the delay one turn at a
        time until the plan fits within the existing reservations. This method
        does not reserve capacity.

        Args:
            route: Ordered sequence of destination zones and connections.

        Returns:
            The timed route plan with the earliest feasible departure.

        Raises:
            ValueError: If the route enters a blocked zone.
        """
        departure_delay = 0
        plan = self._make_plan(route, departure_delay)

        while not self._has_capacity_for_plan(plan):
            departure_delay += 1
            plan = self._make_plan(route, departure_delay)

        return plan

    def schedule_drone(self, drone: Drone, routes: list[Route]) -> None:
        """
        Reserve a route for a drone and record its movements.

        Find the earliest feasible plan for each candidate route, then
        select the plan with the earliest final arrival. If plans have
        the same final arrival turn, select the first one.

        Update zone and connection reservations. Append movements to the
        output. For restricted zones, record the connection crossing one
        turn before the zone arrival. Existing plans remain unchanged.

        Args:
            drone: Drone whose movements will be scheduled.
            routes: Candidate routes to consider.

        Raises:
            ValueError: If no candidate routes are supplied or a candidate
                route enters a blocked zone.
        """
        if not routes:
            raise ValueError("No candidate routes supplied")

        plans = [
            self._find_earliest_plan(route)
            for route in routes
        ]

        plan = min(
            plans,
            key=lambda candidate: candidate[-1][0] if candidate else 0,
        )

        for arrival_turn, destination, connection in plan:
            crossing_turn = arrival_turn

            if destination.zone == "restricted":
                crossing_turn = arrival_turn - 1

            # Reserve zone capacity for arrival turn
            zone_key = (arrival_turn, destination)
            self.zone_reservation[zone_key] = (
                self.zone_reservation.get(zone_key, 0) + 1
            )

            # Reserve connection capacity on the crossing turn
            link_key = (crossing_turn, connection)
            self.link_reservation[link_key] = (
                self.link_reservation.get(link_key, 0) + 1
            )

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
    Build and apply a turn-based movement schedule for drones.

    Use the router to obtain candidate routes and the scheduler to plan
    movement for all drones. Apply the schedule one turn at a time,
    updating drone locations, connection transit, and zone occupancy.

    Attributes:
        graph: Map containing the zones, connections, hubs, and drones.
        router: Route finder used to obtain candidate routes.
        occupancy: Number of drones currently in each zone, excluding
            drones in transit.
        in_transit: Connection labels keyed by the IDs of drones
            currently crossing connections.
        output: Scheduled movements grouped by turn. Each movement
            contains a drone ID and a zone name or connection label.
            Index 0 represents turn 1.
    """
    def __init__(self, graph: Graph, router: Router) -> None:
        """
        Initialize a simulation with a graph and router.

        Index drones by ID and create empty occupancy, transit, and
        movement records. Drone locations are left unchanged.

        Args:
            graph: Map containing the zones, connections, hubs and drones.
            router: Route finder used to obtain candidate routes.
        """
        self.graph = graph
        self.router = router
        self._drones_by_id: dict[int, Drone] = {
            drone.id: drone for drone in graph.drones
        }
        self.occupancy: dict[Zone, int] = {}
        self.in_transit: dict[int, str] = {}
        self.output: SimulationOutput = []
        self._update_occupancy()

    def _get_candidate_routes(self) -> list[Route]:
        """
        Collect the best route and unique alternative routes.

        Start with the router's best route to the end hub. For each
        connection in that route, request an alternative route from the
        start hub, excluding that connection. Ignore missing or duplicate
        alternatives.

        Returns:
            A list containing the best route followed by unique alternatives.
        """
        best = self.router.get_best_route(self.graph.end_hub.name)
        routes: list[Route] = [best]

        for _, connection in best:
            alternative = self.router.get_alternate_route(
                self.graph.start_hub,
                connection,
            )
            if alternative is not None and alternative not in routes:
                routes.append(alternative)

        return routes

    def _build_schedule(self) -> SimulationOutput:
        """
        Build a capacity-aware movement schedule for all drones.

        Use a new scheduler to schedule drones in their graph order,
        considering the same candidate routes for each drone.

        This method does not update drone locations.

        Returns:
            Scheduled movements grouped by turn. Index 0 represents turn 1.
        """
        scheduler = Scheduler(self.graph)
        routes = self._get_candidate_routes()

        for drone in self.graph.drones:
            scheduler.schedule_drone(drone, routes)

        return scheduler.output

    def _apply_turn(self, turn: Turn) -> None:
        """
        Apply one turn of scheduled movements and refresh zone occupancy.

        Treat locations found in the graph's zone lookup as zone arrivals.
        Update those drones' current zones and remove their transit records.
        Treat other locations as connection labels and mark those drones as
        in transit without changing their current zones.

        Args:
            turn: Movements containing a drone ID and a zone name or
                connection label.

        Raises:
            KeyError: If a movement references an unknown drone ID.
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
        Recalculate the number of drones currently in each zone.

        Reset all zone counts, then count each drone at its current zone
        unless the drone is marked as in transit.
        """
        self.occupancy = {
            zone: 0 for zone in self.graph.zones
        }

        for drone in self.graph.drones:
            if drone.id not in self.in_transit:
                self.occupancy[drone.current_zone] += 1

    def run_simulation(self) -> SimulationOutput:
        """
        Build and apply the complete movement schedule.

        Replace the stored output with a newly built schedule, then apply
        each turn to update drone locations, transit records, and occupancy.
        Drone locations are not reset before scheduling.

        Returns:
            Movements grouped by simulation turn. Each movement contains a
            drone identifier and a destination zone or conneciton label. Index
            zero represents a turn one.
        """
        self.output = self._build_schedule()

        for turn in self.output:
            self._apply_turn(turn)

        return self.output
