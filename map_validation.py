from map_config import MapConfig
from error import MapValidationError


class MapValidation():
    """
    Check zone names and connections for consistency

    Attributes:
        config: Map configuration to validate.
    """
    def __init__(self, config: MapConfig) -> None:
        """
        Initialize the validator without running validation.

        Args:
            config: Map configuration to validate
           """
        self.config = config

    def validate(self) -> None:
        """
        Validate zone uniqueness and connection consistency.

        Raises:
            MapValidationError: If zone names repeat, connection endpoints are
                unknown, or connections are duplicated,
        """
        zone_names = self._validate_zone()
        self._validate_connection(zone_names)

    def _validate_zone(self) -> set[str]:
        """
        Check that all zones have uniqe names.

        Raises:
            MapValidationError: If a zone names appears more than once.
        """
        zones = [self.config.start_hub, self.config.end_hub]
        zones.extend(self.config.hub)
        names: set[str] = set()

        for zone in zones:
            if zone.name in names:
                raise MapValidationError(f"Duplicate zone name: {zone.name}")
            names.add(zone.name)

        return names

    def _validate_connection(self, names: set[str]) -> None:
        """
        Check connection endpoints and reject duplicate connections.

        Connections are bidirectional, so A-B and B-A are duplicates.

        Args:
            names: Known zone names used to check connection endpoints.

        Raises:
            MapValidationError: If an endpoint references an unknown zone or
                a connection appears more than once.
        """
        connections: set[tuple[str, str]] = set()

        for connection in self.config.connection:
            start = connection.from_zone
            end = connection.to_zone

            for name in (start, end):
                if name not in names:
                    raise MapValidationError(
                        f"Connection {start}--{end}: unknown zone '{name}'"
                    )

            first, second = sorted((start, end))
            pair = (first, second)
            if pair in connections:
                raise MapValidationError(
                    f"Duplicate connection: "
                    f"{connection.from_zone}--{connection.to_zone}"
                )
            connections.add(pair)
