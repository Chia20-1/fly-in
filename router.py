from models import Graph, Zone


class Router:
    """
    """
    def __init__(self, graph: Graph) -> None:
        """
        """
        self.graph = graph

    def _find_neighbor(self, zone: str) -> list[Zone]:
        """
        """
        neighbors: list[Zone] = []
        zones_by_name: dict[str, Zone] = {
            item.name: item
            for item in self.graph.zones
        }
        for connection in self.graph.adjacency[zone]:
            if connection.from_zone == zone:
                neighbor_name = connection.to_zone
            else:
                neighbor_name = connection.from_zone
            neighbors.append(zones_by_name[neighbor_name])
        return neighbors
