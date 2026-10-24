from map_config import MapConfig, ZoneConfig


class Drone:
    """
    Represent a drone and its current location.

    Attributes:
        id: Indentifier assigned when drone is created.
        current_zone: Zone currently occupied by the drone.
    """
    id: int = 1

    def __init__(self, start_hub: "Zone") -> None:
        self.id = self.__class__.id
        self._new_id()
        self.current_zone = start_hub

    @classmethod
    def _new_id(cls) -> None:
        cls.id += 1


class Zone:
    """
    Represent a zone in the graph.

    Attributes:
        name: Zone name.
        x: Horizontal coordinate.
        y: Vertical coordinate.
        zone: Zone category.
        color: Display color, if specified.
        max_drones: Maximum number of drones allowed in the zone.
    """
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone: str,
        color: str | None,
        max_drones: int
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone: str = zone
        self.color: str | None = color
        self.max_drones: int = max_drones


class Connection:
    """
    Represent a bidirectional connection between two zones.

    Attributes:
        from_zone: Name of one endpoint.
        to_zone: Name of the other endpoint.
        max_link_capacity: Maximum number of drones allowed on the connection.
    """
    def __init__(
        self,
        from_zone: str,
        to_zone: str,
        max_link_capacity: int,
    ) -> None:
        self.from_zone: str = from_zone
        self.to_zone: str = to_zone
        self.max_link_capacity: int = max_link_capacity


class Graph:
    """
    Build the map's zones, connections, and drones from configuration.

    Attributes:
        config: Configuration used to build the graph.
        nb_drones: Number of drones to create.
        zones: All zones in the map.
        connections: Connections between zones.
        drones: Drones initially placed at the starting hub.
        start_hub: Starting zone.
        end_hub: Destination zone.
    """
    def __init__(
        self,
        config: MapConfig,
    ) -> None:
        """
        Create all zones and assign the starting and destination.

        Returns:
            Zones in starting hub, destination hub, then intermediate
            hub order.
        """
        self.config = config
        self.nb_drones = self.config.nb_drones
        self._init_all()

    def _init_all(self) -> None:
        """
        Initialize and store all zones, connections, and drones.
        """
        self.zones = self._init_zones()
        self.connections = self._init_connections()
        self.drones = self._init_drones()
        self.adjacency = self._init_adjacency()

    def _init_drones(self) -> list[Drone]:
        """
        Create the configured number of drones at the starting hub.

        Returns:
            Newly created drones.
        """
        drones: list[Drone] = [
            Drone(self.start_hub)
            for _ in range(self.nb_drones)
        ]
        return drones

    def _init_zones(self) -> list[Zone]:
        """
        Create all zones and assign the starting and destination.

        Returns:
            Zones in starting hub, destination hub, then intermediate hub.
        """
        zone_configs: list[ZoneConfig] = [
            self.config.start_hub,
            self.config.end_hub,
            *self.config.hub
            ]
        zones: list[Zone] = [
            Zone(z.name, z.x, z.y, z.zone, z.color, z.max_drones)
            for z in zone_configs
        ]
        for zone in zones:
            if zone.name == self.config.start_hub.name:
                self.start_hub = zone
            if zone.name == self.config.end_hub.name:
                self.end_hub = zone
        return zones

    def _init_connections(self) -> list[Connection]:
        """
        Create connections from the map configuration.

        Returns:
            Connections with their endpoint names and capacities.
        """
        connections: list[Connection] = [
            Connection(item.from_zone, item.to_zone, item.max_link_capacity)
            for item in self.config.connection
        ]
        return connections

    def _init_adjacency(self) -> dict[str, list[Connection]]:
        """
        Group connections by their endpoint zones.

        Returns:
            A mapping from each zone name to its incident connection.
        """
        adjacency: dict[str, list[Connection]] = {
            zone.name: []
            for zone in self.zones
        }
        for connection in self.connections:
            adjacency[connection.from_zone].append(connection)
            adjacency[connection.to_zone].append(connection)
        return adjacency
