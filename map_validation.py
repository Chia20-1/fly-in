from map_config import MapConfig
from error import MapValidationError


class MapValidation():
    """
    Check zone names and connections for consistency.

    Attributes:
        config: Map configuration to validate.
        line_numbers: Source line numbers grouped by declaration key.
    """
    def __init__(
            self,
            config: MapConfig,
            line_numbers: dict[str, list[int]],
    ) -> None:
        """
        Initialize the validator without running validation.

        Args:
            config: Map configuration to validate
            line_numbers: Source line numbers corresponding to the
                configuration's declarations, in per-key source order.
        """
        self.config = config
        self.line_numbers = line_numbers

    def validate(self) -> None:
        """
        Validate zone uniqueness and connection consistency.

        Raises:
            MapValidationError: If a zone name repeats, a connection endpoint
                is unknown, or a connection is duplicated. Include the invalid
                declaration's source line.
        """
        zone_names = self._validate_zone()
        self._validate_connection(zone_names)

    def _validate_zone(self) -> set[str]:
        """
        Check that all zones have unique names in source-line order.

        Returns:
            The set of unique zone names.

        Raises:
            MapValidationError: If a zone name appears more than once.
        """
        declarations = [
            (
                self.line_numbers["start_hub"][0],
                self.config.start_hub,
            ),
            (
                self.line_numbers["end_hub"][0],
                self.config.end_hub,
            )
        ]
        declarations.extend(
            (self.line_numbers["hub"][index], zone)
            for index, zone in enumerate(self.config.hub)
        )
        declarations.sort(key=lambda item: item[0])
        names: set[str] = set()

        for line_number, zone in declarations:
            if zone.name in names:
                raise MapValidationError(
                    f"on line {line_number}: "
                    f"Duplicate zone name: {zone.name}"
                )
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
                a connection appears more than once, with the invalid
                declaration's line number.
        """
        connections: set[tuple[str, str]] = set()

        for index, connection in enumerate(self.config.connection):
            line_number = self.line_numbers["connection"][index]
            start = connection.from_zone
            end = connection.to_zone

            for name in (start, end):
                if name not in names:
                    raise MapValidationError(
                        f"on line {line_number}: "
                        f"Connection {start}--{end}: unknown zone '{name}'"
                    )

            first, second = sorted((start, end))
            pair = (first, second)
            if pair in connections:
                raise MapValidationError(
                    f"on line {line_number}: "
                    f"Duplicate connection: {start}--{end}"
                )
            connections.add(pair)
