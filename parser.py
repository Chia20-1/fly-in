from error import MapValidationError, MapParserError

class MapParser:
	"""
	"""
	VALID_KEYS = frozenset({
		"nb_drones", "start_hub", "end_hub", "hub", "connection"
	})

	def __init__(self, file_path: str)->None:
		self.file_path = file_path

	def parse(self)->dict:
		raw_map: dict[str, str] = self._read()
		self._check_structure(raw_map)
		return raw_map

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

	def _check_structure(self, raw_map: dict)->None:
		for key in ("start_hub", "end_hub"):
			if len(raw_map.get(key,[])) != 1:
				raise MapParserError(f"Map must contain exactly one {key}")

		if len(raw_map.get("nb_drones",[])) != 1:
			raise MapParserError("Map must contain exactly one nb_drones")

		if not raw_map.get("hub"):
			raise MapParserError("Map must contain at least one hub")
		
		if not raw_map.get("connection"):
			raise MapParserError("Map must contain at least one connection")
