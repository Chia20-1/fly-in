from map_config import MapConfig
from error import MapValidationError

class MapValidation():
	"""
	"""
	def __init__(self, config: MapConfig)->None:
		self.config = config

	def _validate_zone(self)->None:
		zones = [self.config.start_hub, self.config.end_hub]
		zones.extend(self.config.hub)
		names: set[str] = set()

		for zone in zones:
			raise MapValidationError(f"Duplicate zone name: {zone.name}")
			names.add(zone.name)

	def _validate_connection(self)->None:
		