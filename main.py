from map_parser import MapParser
from error import MapValidationError, MapParserError
from map_config import MapConfig
from sys import argv, stderr, exit

def	_get_file()->str:
	if len(argv) != 2:
		print("Usage example: python3 main.py map_file_path.txt")
		exit(1)
	return argv[1]

def _get_raw_map(file_path: str)->dict[str, list[str]]:
	try:
		parser = MapParser(file_path)
		return parser.parse()
	except (MapParserError, MapValidationError) as error:
		print(f"Error: {error}", file=stderr)
		exit(1)

def _get_config(raw_map: dict[str, list[str]])->MapConfig:
	pass

if __name__ == "__main__":
	file_path = _get_file()
	raw_map = _get_raw_map(file_path)
	print(raw_map)
