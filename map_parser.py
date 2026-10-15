from error import MapParserError

class MapParser:
	"""
	"""
	VALID_KEYS = frozenset({
		"nb_drones", "start_hub", "end_hub", "hub", "connection"
	})

	def __init__(self, file_path: str)->None:
		self.file_path = file_path

	def _get_lines(self)->list[str]:
		lines: list[str] = []
		try:
			with open(self.file_path, "r", encoding="utf-8") as file:
				lines = file.readlines()
		except OSError:
			raise MapParserError("Failed to open map file")
		return lines
	
	def _read(self)->dict[str, list[str]]:
		raw_map: dict[str, list[str]] = {}
		lines: list[str] = self._get_lines()

		for line_number, line in enumerate(lines, start=1):
			line = line.strip()
			if not line or line.lstrip().startswith("#"):
				continue
			key, separator, value = line.partition(":")
			if not separator:
				raise MapParserError(
					f"Invalid map line {line_number}: missing ':'"
				)
			key = key.strip()
			if key not in self.VALID_KEYS:
				raise MapParserError(
					f"Invalid map line {line_number}: unknown key '{key}'"
				)
			value = value.strip()
			if not value:
				raise MapParserError(
					f"Invalid map line {line_number}: empty value for '{key}'"
				)
			raw_map.setdefault(key, []).append(value)
		return raw_map

	def _check_structure(self, raw_map: dict[str, list[str]])->None:
		for key in ("start_hub", "end_hub", "nb_drones"):
			if len(raw_map.get(key,[])) != 1:
				raise MapParserError(f"Map must contain exactly one {key}")

		for key in ("hub", "connection"):
			if not raw_map.get(key):
				raise MapParserError("Map must contain at least one {key}")

	def _parse_raw(self)->dict[str, list[str]]:
		raw_map: dict[str, list[str]] = self._read()
		self._check_structure(raw_map)
		return raw_map

	def _parse_metadata(self, metadata: str | None)-> dict[str, str]:
		attributes: dict[str, str] = {}
		if not metadata:
			return attributes
		metadata = metadata.strip()
		if not metadata.startswith("[") or not metadata.endswith("]"):
			raise MapParserError("Invalid metadata brackets")
		content = metadata[1:-1]
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

	def _parse_connection(self, value: str)->dict[str, str]:
		body, opening, metadata = value.partition("[")
		if opening:
			if not body.endswith(" "):
				raise MapParserError("Missing space before metadata")
			body = body[:-1]

		endpoints = body.strip().split("-")
		if len(endpoints) != 2 or not all(endpoints):
			raise MapParserError(f"Invalid connection: {value}")
		if any(char.isspace() for char in body):
			raise MapParserError("Unexpected whitespace in connection")
		from_zone, to_zone = endpoints
		config = {
			"from_zone": from_zone,
			"to_zone": to_zone
		}
		attributes = self._parse_metadata(opening + metadata)
		if config.keys() & attributes.keys():
			raise MapParserError("Metadata conflicts with connection fields")
		config.update(attributes)
		return config

	def _parse_zone(self, value: str)->dict:
		pass


