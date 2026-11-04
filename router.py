from models import Graph, Zone, Connection
import heapq
from typing import TypeAlias


Route: TypeAlias = list[tuple[Zone, Connection]]


class Router:
    """
    Find minimum-cost routes through a graph using Dijkstra's algorithm.

    Search records are created after a search with valid endpoint names
    and describe the latest search, including its chosen starting zone.

    Attributes:
        graph: Graph used to look up neighboring zones.
        cost: Minimum movement cost to each reachable zone.
        priority_count: Number of priority zones on each selected route.
        previous: Predecessor name and connection for each reached zone
            other than the search's starting zone.
    """
    def __init__(self, graph: Graph) -> None:
        """
        Initialize the router with a graph.

        Args:
            graph: Graph containing the zones and adjacency lookup.
        """
        self.graph = graph

    def _find_neighbor(self, zone: str) -> list[Zone]:
        """Return the zones adjacent to the named zone.

        Args:
            zone: Name of the zone whose neighbors to retrieve.

        Returns:
            A list of adjacent Zone objects, including any blocked zones.
            An empty list if the zone has no connections.

        Raises:
            KeyError: If zone is absent from the graph's adjacency lookup.
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

    def _find_route(
        self,
        start: str,
        dest: str,
        excluded_connection: Connection | None = None,
    ) -> Route | None:
        """
        Find a minimum-cost route between two zones.

        Prefer more priority zones when costs tie. Skip blocked destinations
        and the excluded connection in both directions. Replace the stored
        cost, priority_count, and previous records with this search's results.

        Args:
            start: Name of the zone from which to search.
            dest: Name of the destination zone.
            excluded_connection: Existing graph connection to skip.
             If None, exclude no connection.

        Returns:
            Destination-zone and connection pairs in travel order, excluding
            the starting zone. Return an empty list if start equals dest,
            or None if no route exists.

        Raises:
            ValueError: If start or dest is unknown.
        """
        for name in (start, dest):
            if name not in self.graph.zone_lookup:
                raise ValueError(f"Unknown zone '{name}'")

        pending: list[tuple[int, int, str]] = [(0, 0, start)]
        cost: dict[str, int] = {start: 0}
        priority_count: dict[str, int] = {start: 0}
        previous: dict[str, tuple[str, Connection]] = {}

        while pending:
            current_cost, priority, current_name = heapq.heappop(pending)
            current_priority = -priority

            # Ignore entries replaced by a better route.
            if (
                current_cost != cost[current_name]
                or current_priority != priority_count[current_name]
            ):
                continue

            for destination, connection in self.graph.adjacency[current_name]:
                if connection is excluded_connection:
                    continue

                movement_cost = self._movement_cost(destination)
                if movement_cost is None:
                    continue

                destination_name = destination.name
                new_cost = current_cost + movement_cost
                new_priority = current_priority

                if destination.zone == "priority":
                    new_priority += 1

                if (
                    destination_name not in cost
                    or new_cost < cost[destination_name]
                    or (
                        new_cost == cost[destination_name]
                        and new_priority > priority_count[destination_name]
                    )
                ):
                    cost[destination_name] = new_cost
                    priority_count[destination_name] = new_priority
                    previous[destination_name] = (current_name, connection)

                    heapq.heappush(
                        pending,
                        (new_cost, -new_priority, destination_name),
                    )

        # Keep the latest search records available for inspection.
        self.cost = cost
        self.priority_count = priority_count
        self.previous = previous

        if dest not in cost:
            return None

        # Follow predecessors backward, then reverse the route.
        route: Route = []
        current_name = dest

        while current_name != start:
            previous_name, connection = previous[current_name]
            current_zone = self.graph.zone_lookup[current_name]
            route.append((current_zone, connection))
            current_name = previous_name

        route.reverse()
        return route

    def get_best_route(self, dest: str) -> Route:
        """
        Return a minimum-cost route from the start hub.

        Prefer more priority zones when costs tie.

        Args:
            dest: Name of the destination zone.

        Returns:
            Destination-zone and connection pairs in travel order, excluding
            the start hub. Return an empty list if dest is the start hub.

        Raises:
            ValueError: If the destination is unknown or unreachable.
        """
        start = self.graph.start_hub.name
        route = self._find_route(start, dest)

        if route is None:
            raise ValueError(
                f"No valid path from '{start}' to '{dest}'"
            )

        return route

    def get_alternate_route(
        self,
        current_zone: Zone,
        unavailable_connection: Connection,
    ) -> Route | None:
        """
        Find an alternative from the current zone to the end hub.

        Avoid the supplied connection and prefer more priority zones when
        costs tie. Do not move the drone or check live capacity.

        Args:
            current_zone: Zone from which to search.
            unavailable_connection: Existing graph connection to exclude
                in both directions, matched by object identity.

        Returns:
            Minimum-cost route as destination-zone and connection pairs,
            excluding current_zone. Return an empty list if already at the
            end hub, or None if no alternative exists.

        Raises:
            ValueError: If the current zone or end hub name is unknown.
        """
        return self._find_route(
            current_zone.name,
            self.graph.end_hub.name,
            excluded_connection=unavailable_connection,
        )
