from models import Graph, Zone, Connection


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

    def find_route(self) -> list[tuple[Zone, Connection]]:

