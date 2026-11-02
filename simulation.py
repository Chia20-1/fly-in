from models import Graph, Zone
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
        for drone in self.graph.drones:
            index = self.next_step[drone.id]

            if index == self.end:
                continue

            destination, connection = self.route[index]
            