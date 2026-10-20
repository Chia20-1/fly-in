from map_config import MapConfig
from error import MapValidationError

class MapValidation():
	"""
	"""
	def __init__(self, config: MapConfig)->None:
		self.config = config

	def validate(self)->None:
		zone_names = self._validate_zone()
		self._validate_connection(zone_names)

	def _validate_zone(self)->set[str]:
		zones = [self.config.start_hub, self.config.end_hub]
		zones.extend(self.config.hub)
		names: set[str] = set()

		for zone in zones:
			if zone.name in names:
				raise MapValidationError(f"Duplicate zone name: {zone.name}")
			names.add(zone.name)

		return names

	def _validate_connection(self, names: set[str])->None:
		connections: set[tuple[str, str]] = set()

		for connection in self.config.connection:
			start = connection.from_zone
			end = connection.to_zone

			for name in (start, end):
				if name not in names:
					raise MapValidationError(
						f"Connection {start}--{end}: unknown zone '{name}'"
					)

			pair = tuple(sorted((start, end)))
			if pair in connections:
				raise MapValidationError(
					f"Duplicate connection: "
					f"{connection.from_zone}--{connection.to_zone}"
				)
			connections.add(pair)

		