from map_config import MapConfig, ZoneConfig


class Drone:
    """
    """
    id: int = 0

    def __init__(self) -> None:
        self.id = self.__class__.id
        self._new_id()

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
        self.config: MapConfig = config
        self._init_all()

    def _init_all(self) -> None:
        self.drones = self._init_drones()
        self.zones = self._init_zones()
        self.connections = self._init_connections()

    def _init_drones(self) -> list[Drone]:
        """
        """
        nb_drones = self.config.nb_drones
        drones: list[Drone] = []
        for _ in range(nb_drones):
            drone = Drone()
            drones.append(drone)
        return (drones)

    def _init_zones(self) -> list[Zone]:
        """
        """
        zones: list[Zone] = []
        zone_configs: list[ZoneConfig] = [
            self.config.start_hub,
            self.config.end_hub,
            *self.config.hub
        ]
        zones = [
            Zone(z.name, z.x, z.y, z.zone, z.color, z.max_drones)
            for z in zone_configs
        ]
        return zones

    def _init_connections(self) -> list[Connection]:
        """
        """
        connections: list[Connection] = [
            Connection(item.from_zone, item.to_zone, item.max_link_capacity)
            for item in self.config.connection
        ]
        return connections
