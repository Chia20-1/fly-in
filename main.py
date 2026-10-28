from map_parser import MapParser
from map_config import MapConfig
from map_validation import MapValidation
from models import Graph
from pydantic import ValidationError
from error import MapValidationError, MapParserError
from sys import argv, stderr, exit


def _get_file() -> str:
    """
    Get the map file path from the command-line arguments.

    Returns:
        The supplied map file path.

    Raises:
        SystemExit: With status 1 after printing ussage to standard error
            if exactly one argument is provided.
    """
    if len(argv) != 2:
        print("Usage example: python3 main.py map_file_path.txt", file=stderr)
        exit(1)
    return argv[1]


def _get_raw_map(
        file_path: str,
) -> tuple[dict[str, object], dict[str, list[int]]]:
    """
    Read and parse the map file.

    Args:
        file_path: Path to the map file.

    Returns:
        Parsed map data, with numeric values still stored as strings.

    Raises:
        SystemExit: Wtih status 1 after printing a file access, decoding,
            or parsing error to standard error.
    """
    try:
        parser = MapParser(file_path)
        raw_map = parser.parse()
        return raw_map, parser.line_numbers
    except (MapParserError, UnicodeDecodeError) as error:
        print(f"Error: {error}", file=stderr)
        exit(1)


def _get_error_line(
        location: tuple[str | int, ...],
        line_numbers: dict[str, list[int]],
) -> int | None:
    if not location:
        return None

    key = str(location[0])
    index = 0

    if len(location) > 1 and isinstance(location[1], int):
        index = location[1]

    lines = line_numbers.get(key, [])
    if index < 0 or index >= len(lines):
        return None
    return lines[index]


def _get_config(
    raw_map: dict[str, object],
    line_numbers: dict[str, list[int]],
) -> MapConfig:
    """
    Convert raw map data into a configuration and validate its fields.

    Args:
        raw_map: Map data returned by the parser.

    Returns:
        A configuration with converted types, validated fields, and defaults.

    Raises:
        SystemExit: With status 1 after printing field validation errors
            to standard error.
    """
    try:
        return MapConfig.model_validate(raw_map)
    except ValidationError as error:
        for detail in error.errors():
            field = " ".join(map(str, detail["loc"]))
            line = _get_error_line(detail["loc"], line_numbers)
            prefix = f"Error on line {line}" if line is not None else "Error"
            print(f"{prefix}: {field}: {detail['msg']}", file=stderr)
        exit(1)


def _validate_config(config: MapConfig) -> None:
    """
    Check zone uniqueness and connection consistency.

    Args:
        config: Map configuration with validated field values.

    Raises:
        SystemExit: With status 1 after printing a validation error to
            standard error if zone names repeat, connection endpoints
            are unknown, or connections are duplicated.
    """
    try:
        validation = MapValidation(config)
        validation.validate()
    except MapValidationError as error:
        print(f"Error: {error}", file=stderr)
        exit(1)


if __name__ == "__main__":
    file_path = _get_file()
    raw_map, line_numbers = _get_raw_map(file_path)
    config = _get_config(raw_map, line_numbers)
    _validate_config(config)
    graph = Graph(config)
    print(graph.adjacency)
