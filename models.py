from map_config import MapConfig, ZoneConfig


class Drone:
    """
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
    """
    def __init__(
        self,
        config: MapConfig,
    ) -> None:
        self.config = config
        self.nb_drones = self.config.nb_drones
        self._init_all()

    def _init_all(self) -> None:
        self.zones = self._init_zones()
        self.connections = self._init_connections()
        self.drones = self._init_drones()

    def _init_drones(self) -> list[Drone]:
        """
        """
        drones: list[Drone] = [
            Drone(self.start_hub)
            for _ in range(self.nb_drones)
        ]
        return drones

    def _init_zones(self) -> list[Zone]:
        """
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
        """
        connections: list[Connection] = [
            Connection(item.from_zone, item.to_zone, item.max_link_capacity)
            for item in self.config.connection
        ]
        return connections

    def _init_adjacency(self) -> dict[str, list[Connection]]:
        """
        """
        adjacency: dict[str, list[Connection]] = {
            zone.name: []
            for zone in self.zones
        }
        for connection in self.connections:
            adjacency[connection.from_zone].append(connection)
            adjacency[connection.to_zone].append(connection)
        return adjacency