from pydantic import BaseModel, Field
from error import MapValidationError


class RawConfig(BaseModel):
	@staticmethod
	def _parse_metadata(metadata: str) -> dict[str, str]:
		attributes: dict[str, str] = []
		if not metadata:
			return attributes

class ZoneConfig(BaseModel):
	name: str
	x: int
	y: int


class ConnectionConfig(BaseModel):
	from_zone: str
	to_zone: str


class MapConfig(BaseModel):
	nb_drones: int = Field(gt=0)
	start_hub: ZoneConfig
	end_hub: ZoneConfig
	hub: list[ZoneConfig]
	connection: list[ConnectionConfig]
