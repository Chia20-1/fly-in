from models import Graph, Zone, Connection
import heapq
from typing import TypeAlias


Route: TypeAlias = list[tuple[Zone, Connection]]


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
        Compute shortest movement costs from the starting hub using Dijkstra.
        Among equal-cost paths, prefer paths that enter more priority zones.

        Pending stores zones waiting to be explored. Cost stores the lowest
        cost found to reach each zone. Priority count tracks how many priority
        zones are on each chosen path. Previous stores where we came from and
        which connection we used, so we can rebuild the final route.

        Returns:
            A dictionary mapping reachable zone names to minimum total
            movement costs in turns. The starting hub has cost zero;
            unreachable and blocked zones are omitted.
        """
        start_name = self.graph.start_hub.name

        pending: list[tuple[int, int, str]] = [(0, 0, start_name)]
        cost: dict[str, int] = {start_name: 0}
        priority_count: dict[str, int] = {start_name: 0}
        previous: dict[str, tuple[str, Connection]] = {}

        # heappop always choose lowest cost first
        while pending:
            current_cost, priority, current_name = heapq.heappop(pending)
            current_priority = -priority

            # Reject outdated entries
            if (
                current_cost > cost[current_name]
                or current_priority != priority_count[current_name]
            ):
                continue

            for destination, connection in self.graph.adjacency[current_name]:
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

        self.cost = cost
        self.priority_count = priority_count
        self.previous = previous
        return self.cost

    def _available_steps(
        self,
        current: str,
        visited: set[str],
    ) -> Route:
        """
        Return unvisited, traversable steps from the current zone.

        Args:
            current: Name of the zone whose connections to examine.
            visited: Names of zones to exclude from the available steps.

        Returns:
            A list of pairs containing an adjacent zone and the connection
            used to enter it. Visited and blocked zones are excluded.
            The list is empty if no eligible steps exist.

        Raises:
            KeyError: If current is absent from the graph's adjacency lookup.
        """
        steps: Route = []
        for destination, connection in self.graph.adjacency[current]:
            if destination.name in visited:
                continue
            if self._movement_cost(destination) is None:
                continue
            steps.append((destination, connection))
        return steps

    def _explore_routes(
        self,
        current: str,
        dest: str,
        visited: set[str],
    ) -> list[Route]:
        """
        Find all traversable routes from the current zone to a destination.

        Explore routes using depth-first search, excluding blocked zones and
        zones already visited on each path. Leave the supplied visited set
        unchanged.

        Args:
            current: Name of the zone from which to explore routes.
            dest: Name of the destination zone.
            visited: Names of zones already visited on the path. Include
                current to prevent routes from returning to the initial zone.

        Returns:
            A list of routes, each containing pairs of zones to enter and
            connections to use, in travel order. The initial zone is excluded.
            Return an empty list if no route exists, or a list containing one
            empty route if current equals dest. Routes are not sorted by cost.

        Raises:
            KeyError: If a zone being explored is absent from the graph's
                adjacency lookup.
        """
        path: Route = []
        routes: list[Route] = []
        pending: list[tuple[str, Route, set[str]]] = [
            (current, path, visited)
        ]
        while pending:
            current, path, visited = pending.pop()

            if current == dest:
                routes.append(path)
                continue

            for destination, connection in self._available_steps(
                current, visited
            ):
                next_path: Route = path + [(destination, connection)]
                next_visited: set[str] = visited | {destination.name}
                pending.append(
                    (destination.name, next_path, next_visited)
                )
        return routes

    def get_best_route(self, dest: str) -> Route:
        """
        Return a minimum-cost route from the starting hub to a destination.

        Prefer routes with more priority zones when movement costs are equal.
        Recompute routing records before reconstructing the chosen route.

        Args:
            dest: Name of the destination zone.

        Returns:
            A list of steps in travel order, each containing the zone to enter
            and the connection used to enter it. The starting hub is excluded.
            Return an empty list if the destination is the starting hub.

        Raises:
            ValueError: If the destination is unknown or unreachable.
        """
        self._get_cost()

        if dest not in self.cost:
            raise ValueError("No valid path from start hub "
                             f"'{self.graph.start_hub.name}' to "
                             f"destination '{dest}'")

        route: Route = []
        current_name: str = dest
        start_name: str = self.graph.start_hub.name

        while current_name != start_name:
            previous_name, connection = self.previous[current_name]
            current_zone = self.graph.zone_lookup[current_name]

            route.append((current_zone, connection))
            current_name = previous_name

        route.reverse()
        return route

    def get_routes(self, dest:str) -> list[Route]:
        """
        Return all traversable routes from the starting hub to a destination.

        Exclude blocked zones and routes that revisit a zone. Routes are not
        sorted by movement cost or priority-zone count.

        Args:
            dest: Name of the destination zone.

        Returns:
            A list of routes, each containing pairs of zones to enter and
            connections to use, in travel order. The starting hub is excluded.
            Return a list containing one empty route if dest is the starting
            hub.

        Raises:
            ValueError: If the destination is unknown or unreachable.
        """
        if dest not in self.graph.zone_lookup:
            raise ValueError(f"Unknow destination '{dest}'")
        start: str = self.graph.start_hub.name
        visited: set[str] = {start}
        routes = self._explore_routes(start, dest, visited)
        if not routes:
            raise ValueError(f"No valid path from '{start}' to '{dest}'")
        return routes
