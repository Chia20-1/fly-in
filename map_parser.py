from error import MapParserError


class MapParser:
    """
    """
    VALID_KEYS = frozenset({
        "nb_drones", "start_hub", "end_hub", "hub", "connection"
    })

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def parse(self) -> dict[str, object]:
        raw_map = self._parse_raw()

        config_dict = {
           "nb_drones": raw_map["nb_drones"][0][1],
           "start_hub": self._parse_entries("start_hub", raw_map)[0],
           "end_hub": self._parse_entries("end_hub", raw_map)[0],
           "hub": self._parse_entries("hub", raw_map),
           "connection": self._parse_entries("connection", raw_map),
        }
        return config_dict

    def _get_lines(self) -> list[str]:
        lines: list[str] = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except OSError:
            raise MapParserError("Failed to open map file")
        return lines

    def _read(self) -> dict[str, list[tuple[int, str]]]:
        raw_map: dict[str, list[tuple[int,str]]] = {}
        lines: list[str] = self._get_lines()

        for line_number, line in enumerate(lines, start=1):
            line = line.removesuffix("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            key, separator, value = line.partition(":")
            if not separator:
                raise MapParserError(
                    f"Invalid map line {line_number}: missing ':'"
                )
            if key not in self.VALID_KEYS:
                raise MapParserError(
                    f"Invalid map line {line_number}: unknown key '{key}'"
                )
            if not value.startswith(" "):
                raise MapParserError(
                    f"Invalid map line {line_number}: missing space after ':'"
                )
            value = value[1:]
            if value != value.strip():
                raise MapParserError(
                    f"Invalid map line {line_number}: "
                    f"unexpected whitesapce around value for '{key}'"
                )
            if not value:
                raise MapParserError(
                    f"Invalid map line {line_number}: empty value for '{key}'"
                )
            raw_map.setdefault(key, []).append((line_number,value))
        return raw_map

    def _check_structure(self, raw_map: dict[str, list[tuple[int,str]]]) -> None:
        for key in ("start_hub", "end_hub", "nb_drones"):
            if len(raw_map.get(key, [])) != 1:
                raise MapParserError(f"Map must contain exactly one {key}")

        for key in ("hub", "connection"):
            if not raw_map.get(key):
                raise MapParserError(f"Map must contain at least one {key}")

    def _parse_raw(self) -> dict[str, list[tuple[int,str]]]:
        raw_map: dict[str, list[tuple[int,str]]] = self._read()
        self._check_structure(raw_map)
        return raw_map

    def _parse_metadata(self, metadata: str | None) -> dict[str, str]:
        attributes: dict[str, str] = {}
        if not metadata:
            return attributes
        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise MapParserError("Invalid metadata brackets")
        content = metadata[1:-1]
        if content != " ".join(content.split()):
            raise MapParserError("Invalid whitespace in metadata")
        for item in content.split():
            if item.count("=") != 1:
                raise MapParserError(f"Invalid metadata: {item}")
            key, separator, value = item.partition("=")
            if not separator or not key or not value:
                raise MapParserError(f"Invalid metadata: {item}")
            if key in attributes:
                raise MapParserError(f"Duplicate metadata: {key}")
            attributes[key] = value
        return attributes

    def _parse_connection(self, value: str) -> dict[str, str]:
        body, separator, metadata = value.partition("[")
        if separator:
            if not body.endswith(" "):
                raise MapParserError("Missing space before metadata")
            body = body[:-1]

        endpoints = body.split("-")
        if len(endpoints) != 2 or not all(endpoints):
            raise MapParserError(f"Invalid connection: {value}")
        if any(char.isspace() for char in body):
            raise MapParserError("Unexpected whitespace in connection")
        from_zone, to_zone = endpoints
        config = {
            "from_zone": from_zone,
            "to_zone": to_zone
        }
        attributes = self._parse_metadata(separator + metadata)
        conflicts = config.keys() & attributes.keys()
        if conflicts:
            raise MapParserError(f"Conflicting metadata fields {conflicts}")
        self._validate_metadata_keys(attributes, {"max_link_capacity"})
        config.update(attributes)
        return config

    def _parse_zone(self, value: str) -> dict[str, str]:
        body, separator, metadata = value.partition("[")
        if separator:
            if not body.endswith(" "):
                raise MapParserError("Missing space before metadata")
            body = body[:-1]

        items = body.split()
        if len(items) != 3:
            raise MapParserError(f"Invalid zone: {value}")
        if body != " ".join(items):
            raise MapParserError(f"Invalid whitespace in zone: {value}")
        zone_name, x_coord, y_coord = items
        config = {
            "name": zone_name,
            "x": x_coord,
            "y": y_coord
        }
        attributes = self._parse_metadata(separator + metadata)
        conflicts = config.keys() & attributes.keys()
        if conflicts:
            raise MapParserError(f"Conflicting metadata fields {conflicts}")
        self._validate_metadata_keys(
            attributes,
            {"zone", "color", "max_drones"}
        )
        config.update(attributes)
        return config

    def _parse_entries(
            self,
            key: str,
            raw_map: dict[str, list[tuple[int, str]]],
    ) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []

        for line_number, value in raw_map.get(key, []):
            try:
                if key == "connection":
                    entry = self._parse_connection(value)
                else:
                    entry = self._parse_zone(value)
            except MapParserError as error:
                raise MapParserError(
                    f"Invalid map line {line_number}: {error}"
                ) from error

            entries.append(entry)
        return entries

    def _validate_metadata_keys(self,
                                attributes: dict[str, str],
                                allowed_keys: set[str]) -> None:
        invalid_keys = attributes.keys() - allowed_keys
        if invalid_keys:
            raise MapParserError(f"Invalid metadata fields: {invalid_keys}")
