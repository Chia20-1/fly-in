from map_parser import MapParser
from map_config import MapConfig
from map_validation import MapValidation
from models import Graph
from router import Router
from simulation import Simulation
from pydantic import ValidationError
from error import MapValidationError, MapParserError
from sys import argv, stderr, exit


def _get_file() -> str:
    """
    Get the map file path and validate the command-line arguments.

    Returns:
        The supplied map file path.

    Raises:
        SystemExit: With status 1 after printing an error or usage message
            if arguments do not match a map path followed by an optional
            '--visual' flag.
    """
    if len(argv) not in (2, 3):
        print("Usage example: python3 main.py map.txt", file=stderr)
        exit(1)
    if len(argv) == 3 and argv[2] != "--visual":
        print(f"Error: Unknown option '{argv[2]}'", file=stderr)
        print("Usage example: python3 main.py map.txt --visual", file=stderr)
        exit(1)
    return argv[1]


def is_visual() -> bool:
    """Return whether the visualization flag was supplied."""
    return len(argv) == 3 and argv[2] == "--visual"


def _get_raw_map(
        file_path: str,
) -> tuple[dict[str, object], dict[str, list[int]]]:
    """
    Read and parse the map file.

    Args:
        file_path: Path to the map file.

    Returns:
        A pair containing parsed map data, with numeric values still stored
        as strings, and a mapping of field names to source line numbers.

    Raises:
        SystemExit: With status 1 after printing a file access, decoding,
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
    """
    Find the source line associated with a validation error.

    Args:
        location: Pydantic error location containing a field name and
            optionally an entry_index.
        line_numbers: Mapping of field names to source line numbers.

    Returns:
        The corresponding source line number, or None if the location
        cannot be matched.
    """
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
        line_numbers: Mapping of field names to source line numbers,
            used to report where validation errors occurred.

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


def _validate_config(
        config: MapConfig,
        line_numbers: dict[str, list[int]]
) -> None:
    """
    Check zone uniqueness and connection consistency.

    Args:
        config: Map configuration with validated field values.
        line_numbers: Source line numbers grouped by declaration key.

    Raises:
        SystemExit: With status 1 after printing a validation error and
            its source line to standard error.
    """
    try:
        validation = MapValidation(config, line_numbers)
        validation.validate()
    except MapValidationError as error:
        print(f"Error {error}", file=stderr)
        exit(1)


if __name__ == "__main__":
    file_path = _get_file()
    visual = is_visual()
    raw_map, line_numbers = _get_raw_map(file_path)
    config = _get_config(raw_map, line_numbers)
    _validate_config(config, line_numbers)
    graph = Graph(config)
    try:
        router = Router(graph)
        simulation = Simulation(graph, router)
        output = simulation.run_simulation()
    except ValueError as e:
        print(f"Error: {e}", file=stderr)
        exit(1)
    if visual:
        from pygame import error as PygameError
        from renderer import Renderer

        try:
            renderer = Renderer(graph, output)
            renderer.run()
        except PygameError as error:
            print(f"Graphics error: {error}", file=stderr)
            exit(1)
    else:
        from text_output import TextOutput
        text_output = TextOutput(output)
        text_output.print_output()
