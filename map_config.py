from pydantic import BaseModel, Field
from typing import Literal


class ZoneConfig(BaseModel):
    """
    Define a zone's properties.

    Attributes:
        name: Zone name.
        x: Horizontal coordinate.
        y: Vertical coordinate.
        zone: Zone category: normal, blocked, restricted, or priority.
            Defaults to normal.
        color: Optional display color. Defaults to None.
        max_drones: Maximum number of drones allowed in the zone.
            Must be positive. Defaults to 1.
    """
    name: str
    x: int
    y: int
    zone: Literal["normal", "blocked", "restricted", "priority"] = "normal"
    color: str | None = None
    max_drones: int = Field(default=1, gt=0)


class ConnectionConfig(BaseModel):
    """
    Define a bidirectional connection between two zones.

    Attributes:
        from_zone: Name of one endpoint zone.
        to_zone: Name of the other endpoint zone.
        max_link_capacity: Maximum number of drones allowed on the
            connection. Must be positive. Defaults to 1.
    """
    from_zone: str
    to_zone: str
    max_link_capacity: int = Field(default=1, gt=0)


class MapConfig(BaseModel):
    """
    Defines the drone count, zones, and connections of a map.

    Attributes:
        nb_drones: Number of drones present in a map. Must be positive.
        start_hub: Starting zone for all drones.
        end_hub: Destination zone for all drones.
        hub: Intermediate zones.
        connection: Connection between zones.
    """
    nb_drones: int = Field(gt=0)
    start_hub: ZoneConfig
    end_hub: ZoneConfig
    hub: list[ZoneConfig]
    connection: list[ConnectionConfig]
