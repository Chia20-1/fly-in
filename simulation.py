from models import Connection, Drone, Graph, Zone
from router import Route


class Simulation:
    """
    """
    def __init__(self, graph: Graph, route: Route) -> None:
        """
        """
        self.graph = graph
        self.route = route
        self.end: int = len(self.route)
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

    def _update_simulation(self) -> None:
        link_usage: dict[Connection, int] = {}
        planned_occupancy = self.occupancy.copy()
        departures: list[tuple[Drone, Zone, Donnction]] = []

        ordered_drones = sorted(
            self.graph.drones,
            key=lambda drone: self.next_step[drone.id],
            reverse=True,
        )

        for drone in ordered_drones:
            index = self.next_step[drone.id]

            # Safeguard of invalid movement
            assert 0 <= index <=self.end, "Route index is out of bounds"

            # 1. Has the drone finished its route?
            if index == self.end:
                continue

            # 2. Has the restricted movement complete?
            if drone.id in self.in_transit:
                continue

            destination, connection = self.route[index]

            # 3. Is the destination blocked?
            if destination.zone == "blocked":
                continue

            # 4. Is the destination full?
            is_ignored_zone = (
                destination is self.graph.start_hub
                or destination is self.graph.end_hub
            )

            if (
                not is_ignored_zone
                and self.occupancy[destination] >= destination.max_drones
            ):
                continue

            # 5. Is the connection full?
            used = link_usage.get(connection, 0)
            if used >= connection.max_link_capacity:
                continue

            # 6. Movement operation
            planned_occupancy[drone.current_zone] -= 1
            planned_occupancy[destination] += 1
            link_usage[conection] = used + 1
            departures.append((drone, destination, connection))

        # Complete restricted movements from last turn
        for drones in self.graph.drones:
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
