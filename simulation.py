from models import Connection, Drone, Graph, Zone
from router import Route, Router


class Simulation:
    """
    """
    def __init__(self, graph: Graph, router: Router) -> None:
        """
        """
        self.graph = graph
        self.router = router

        initial_route = router.get_best_route(graph.end_hub.name)

        self.routes: dict[int, Route] = {
            drone.id: initial_route.copy()
            for drone in graph.drones
        }
        self.next_step: dict[int, int] = {}
        self.occupancy: dict[Zone, int] = {}
        self.in_transit: dict[int, tuple[Zone, Connection]] = {}

    def _init_simulation(self) -> None:
        """
        """
        for drone in self.graph.drones:
            self.next_step[drone.id] = 0

        for zone in self.graph.zones:
            self.occupancy[zone] = 0
            if zone == self.graph.start_hub:
                self.occupancy[zone] = len(self.graph.drones)

    def _can_move(
        self,
        destination: Zone,
        connection: Connection,
        planned_occupancy: dict[Zone, int],
        link_usage: dict[Connection, int],
    ) -> bool:
        """
        """
        if destination.zone == "blocked":
            return False

        unlimited_capacity = (
            destination is self.graph.start_hub
            or destination is self.graph.end_hub
        )

        if (
            not unlimited_capacity
            and planned_occupancy[destination] >= destination.max_drones
        ):
            return False

        used = link_usage.get(connection, 0)
        return used < connection.max_link_capacity

    def _find_usable_alternative(
        self,
        drone: Drone,
        unavailable_connection: Connection,
        planned_occupancy: dict[Zone, int],
        link_usage: dict[Connection, int],
    ) -> Route | None:
        """
        Return an alternative whose first movement can be approved.
        """
        alternative = self.router.get_alternate_route(
            drone.current_zone,
            unavailable_connection,
        )

        if alternative is None:
            return None

        # A delivered drone has no next movement to propose.
        if not alternative:
            return None

        destination, connection = alternative[0]

        if not self._can_move(
            destination,
            connection,
            planned_occupancy,
            link_usage,
        ):
            return None

        return alternative

    def _update_simulation(self) -> None:
        link_usage: dict[Connection, int] = {}

        # Counts occupied slots AND slots reserved by incoming drones.
        planned_occupancy = self.occupancy.copy()
        departures: list[tuple[Drone, Zone, Connection]] = []

        # On a shared route, plan drones nearer the end first.
        # Their departures can free space for drones behind them.
        ordered_drones = sorted(
            self.graph.drones,
            key=lambda drone: 
            (
                len(self.routes[drone.id]) - self.next_step[drone.id],
                drone.id,
            ),
        )

        for drone in ordered_drones:
            route = self.routes[drone.id]
            index = self.next_step[drone.id]

            # Safeguard of invalid movement
            assert 0 <= index <= len(route), "Route index is out of bounds"

            # 1. Has the drone finished its route?
            if drone.current_zone is self.graph.end_hub:
                continue

            # 2. Has the restricted movement complete?
            if drone.id in self.in_transit:
                continue

            assert index < len(route), "Route ended before the end hub"

            destination, connection = route[index]

            if not self._can_move(
                destination,
                connection,
                planned_occupancy,
                link_usage,
            ):
                alternative = self._find_usable_alternative(
                    drone,
                    connection,
                    planned_occupancy,
                    link_usage,
                )

                if alternative is None:
                    continue
                
                # Replace the route
                self.routes[drone.id] = alternative
                self.next_step[drone.id] = 0
                destination, connection = alternative[0]

            # 6. Movement operation
            # Move from source to destination
            # Destination zone is reserved for restricted movement
            planned_occupancy[drone.current_zone] -= 1
            planned_occupancy[destination] += 1
            link_usage[connection] = link_usage.get(connection, 0) + 1
            departures.append((drone, destination, connection))

        # Complete restricted movements from last turn
        for drone in self.graph.drones:
            if drone.id in self.in_transit:
                destination, _ = self.in_transit.pop(drone.id)
                drone.current_zone = destination
                self.next_step[drone.id] += 1
        
        # Run approved movements.
        for drone, destination, connection in departures:
            if destination.zone == "restricted":
                self.in_transit[drone.id] = (destination, connection)
            else:
                drone.current_zone = destination
                self.next_step[drone.id] += 1
        
        self.occupancy = planned_occupancy

    def run_simulation(self) -> int:
        """
        Run until every drone finishes and return the turn count.
        """
        self._init_simulation()
        turns = 0

        while any(
            drone.current_zone is not self.graph.end_hub
            for drone in self.graph.drones
        ):
            self._update_simulation()
            turns += 1

        return turns
