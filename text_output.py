from simulation import SimulationOutput


class TextOutput:
    """
    Display drone simulation movements as text.

    Attributes:
        output: Movement records grouped by simulation turn.
    """
    def __init__(self, output: SimulationOutput) -> None:
        """
        Initialize the text output with simulaiton results.

        Args:
            output: Turns containing (drone_id, destination) movement pairs.
        """
        self.output = output

    def print_output(self) -> None:
        """
        Print each turn's movements.

        Format each movements as 'D<drone_id>-<destination>', with movements
        separated by spaces. Each turns is separated with line break.
        """
        for turn in self.output:
            for movement in turn:
                drone_id, destination = movement
                print(f"D{drone_id}-{destination}", end=" ")
            print()
