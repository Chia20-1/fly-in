from simulation import SimulationOutput
from models import Graph
import pygame


COLORS = {
    "red": "#FF0000",
    "green": "#00FF00",
    "yellow": "#FFFF00",
    "blue": "#0000FF",
    "gray": "#808080",
    "white": "#FFFFFF",
    "black": "#000000",
    "orange": "#FFA500",
    "purple": "#800080",
    "pink": "#FFC0CB",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "brown": "#A52A2A",
}


class TextOutput:
    """
    """
    def __init__(self, output: SimulationOutput, turns: int) -> None:
        """
        """
        self.output = output
        self.turns = turns

    def print_output(self) -> None:
        for turn in self.output:
            for movement in turn:
                drone_id, destination = movement
                print(f"D{drone_id}-{destination}", end=" ")
            print()
        print(f"Turns: {self.turns}")


"""
Pygame concept     |  What you'll use it for                    |
pygame.display     |  Create a visualization window             |
pygame.draw	       |  Draw zones and connections                |
pygame.font	       |  Show zone names and drone IDs             |
pygame.event       |  Detect keyboard input and window closing  |
pygame.time.Clock  |  Control animation frame rate	            |
"""


class Renderer:
    """
    """
    def __init__(
            self,
            graph: Graph,
            output: SimulationOutput
    ) -> None:
        """
        """
        self.graph = graph
        self.output = output
        self._init_display_state()

    def _init_display_state(self) -> None:
        """
        """
        self.current_turn = 0
        self.width = 1200
        self.height = 800
        self.margin = 60
        self.radius = 14
        self.header_height = 80
        self.footer_height = 100
        self.available_width = self.width - (2 * self.margin)
        self.available_height = (
            self.height
            - self.header_height
            - self.footer_height
            - 2 * self.margin
        )
        self._update_positions()

    def _start(self) -> None:
        """
        """
        pygame.init()
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Fly-In")
        self.clock = pygame.time.Clock()

    def _update_positions(self) -> None:
        """
        """
        self.positions: dict[int, str] = {
            drone.id: self.graph.start_hub.name
            for drone in self.graph.drones
        }

        for turn in self.output[:self.current_turn]:
            for drone_id, location in turn:
                self.positions[drone_id] = location

    def _set_turn(self, turn: int) -> None:
        if 0 <= turn <= len(self.output):
            self.current_turn = turn
            self._update_positions()

    def configure_layout(self) -> None:
        """
        """
        pass

    def to_screen(self) -> None:
        """
        """
        pass

    def draw(self, output: SimulationOutput, turns: int) -> None:
        """
        """
        pass

    def run(self) -> None:
        """
        """
        pass
