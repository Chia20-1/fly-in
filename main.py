from map_parser import MapParser
from map_config import MapConfig
from map_validation import MapValidation
from models import Graph
from pydantic import ValidationError
from error import MapValidationError, MapParserError
from sys import argv, stderr, exit


def _get_file() -> str:
    if len(argv) != 2:
        print("Usage example: python3 main.py map_file_path.txt")
        exit(1)
    return argv[1]


def _get_raw_map(file_path: str) -> dict[str, object]:
    try:
        parser = MapParser(file_path)
        return parser.parse()
    except (MapParserError, MapValidationError) as error:
        print(f"Error: {error}", file=stderr)
        exit(1)


def _get_config(raw_map: dict[str, object]) -> MapConfig:
    try:
        config = MapConfig.model_validate(raw_map)
        return (config)
    except ValidationError as error:
        for detail in error.errors():
            field = " ".join(map(str, detail["loc"]))
            print(f"Error: {field}: {detail['msg']}", file=stderr)
        exit(1)


def _validate_config(config: MapConfig) -> None:
    try:
        validation = MapValidation(config)
        validation.validate()
    except MapValidationError as error:
        print(f"Error: {error}", file=stderr)
        exit(1)


if __name__ == "__main__":
    file_path = _get_file()
    raw_map = _get_raw_map(file_path)
    config = _get_config(raw_map)
    _validate_config(config)
    graph = Graph(config)
