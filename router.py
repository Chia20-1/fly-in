from models import Graph, Zone, Connection
import heapq

class Router:
    """
    Provide neighbor lookups and movement costs for a graph.

    Attributes:
        graph: Graph used to look up neighboring zones.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initialize the router with a graph.

        Args:
            graph: Graph containing the zones and adjacency lookup.
        """
        self.graph = graph

    def _find_neighbor(self, zone: str) -> list[Zone]:
        """
        Return the zones adjacent to the named zone.

        Args:
            zone: Name of the zone whose neighbors to retrieve.

        Returns:
            A list of adjacent Zone objects, including any blocked zones.
            An empty list if the zone has no connections.
        """
        neighbors: list[Zone] = []
        for neighbor, _ in self.graph.adjacency[zone]:
            neighbors.append(neighbor)
        return neighbors

    def _movement_cost(self, destination: Zone) -> int | None:
        """
        Return the cost of entering a zone, or None if blocked.

        Args:
            destination: Zone to enter.

        Returns:
            2 for a restricted zone, None for a blocked zone, or 1 otherwise.
        """
        if destination.zone == "blocked":
            return None
        if destination.zone == "restricted":
            return 2
        return 1

    def _get_cost(self) -> dict[str, int]:
        """
        Compute and save shortest costs from the starting hub.
        """
        start_name = self.graph.start_hub.name

        pending: list[tuple[int, str]] = [(0, start_name)]
        cost: dict[str, int] = {start_name: 0}
        previous: dict[str, tuple[str, Connection]] = {}

        while pending:
            current_cost, current_name = heapq.heappop(pending)

            if current_cost > cost[current_name]:
                continue

            for neighbor, connection in self.graph.adjacency[current_name]:
                movement_cost = self._movement_cost(neighbor)

                if movement_cost is None:
                    continue

                neighbor_name = neighbor.name
                new_cost = current_cost + movement_cost

                if (
                    neighbor_name not in cost
                    or new_cost < cost[neighbor_name]
                ):
                    cost[neighbor_name] = new_cost
                    previous[neighbor_name] = (current_name, connection)
                    heapq.heappush(pending, (new_cost, neighbor_name))

        self.cost = cost
        self.previous = previous
        return self.cost
