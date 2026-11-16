from pydantic import BaseModel, BeforeValidator, Field
from typing import Annotated, Literal


def _validate_integer(value: object) -> int:
    """
    Accept an integer or a string containing an integer.

    Args:
        value: Raw value to validate before Pydantic conversion.

    Returns:
        The validated integer.

    Raises:
        ValueError: If the value does not represent an integer.
    """
    if isinstance(value, bool):
        raise ValueError("Expected an integer, not a boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        digits = value
        if digits.startswith(("+", "-")):
            digits = digits[1:]
        if digits.isascii() and digits.isdecimal():
            return int(value)
    raise ValueError("Expected an integer without a decimal point"
                     " or exponent.")


IntegerValue = Annotated[int, BeforeValidator(_validate_integer)]


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
    x: IntegerValue
    y: IntegerValue
    zone: Literal["normal", "blocked", "restricted", "priority"] = "normal"
    color: str | None = None
    max_drones: IntegerValue = Field(default=1, gt=0)


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
    max_link_capacity: IntegerValue = Field(default=1, gt=0)


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
    nb_drones: IntegerValue = Field(gt=0)
    start_hub: ZoneConfig
    end_hub: ZoneConfig
    hub: list[ZoneConfig]
    connection: list[ConnectionConfig]
