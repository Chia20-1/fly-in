from parser import MapParser
from error import MapValidationError, MapParserError
from sys import argv, stderr, exit

def	_get_file()->str:
	if len(argv) != 2:
		print("Usage example: python3 main.py map_file_path.txt")
		exit(1)
	return argv[1]

if __name__ == "__main__":
	file = _get_file()
	try:
		parser = MapParser(file)
		raw_map = parser.parse()
	except (MapParserError, MapValidationError) as error:
		print(f"Error: {error}", file=stderr)
		exit(1)
	print(raw_map)