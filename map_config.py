from pydantic import BaseModel, Field, ValidationError
from sys import stderr, exit
from typing import Literal
from error import MapValidationError


class ZoneConfig(BaseModel):
	name: str
	x: int
	y: int
	zone: Literal["normal", "blocked", "restricted", "priority"] = "normal"
	color: str | None = None
	max_drones: int = Field(default=1, gt=0)


class ConnectionConfig(BaseModel):
	from_zone: str
	to_zone: str
	max_link_capacity: int = Field(default=1, gt=0)


class MapConfig(BaseModel):
	nb_drones: int = Field(gt=0)
	start_hub: ZoneConfig
	end_hub: ZoneConfig
	hub: list[ZoneConfig]
	connection: list[ConnectionConfig]
