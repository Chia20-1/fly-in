from simulation import SimulationOutput
from models import Graph
import pygame
import math


COLORS = {
    "red": "#FF0000",
    "green": "#008000",
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
    "lime": "#b9ff66",
    "gold": "#FFD700",
    "charcoal": "#202020",
}


class Renderer:
    """
    Display simulation turns in an interactive Pygame window.

    Show the map, occupied zones, and movement messages. Provide buttons for
    navigating between turns.

    Attributes:
        graph: Map containing zones, connections, and drones.
        output: Movement records grouped by simulation turn.
    """
    def __init__(
            self,
            graph: Graph,
            output: SimulationOutput
    ) -> None:
        """
        Initialize the renderer with a map and simulation results.

        Args:
            graph: Map containing the zones, connections, and drones
                to display.
            output: Turns containing (drone_id, destination) movement
                pairs.
        """
        self.graph = graph
        self.output = output

    def _init_layout(self) -> None:
        """Calculate layout dimensions from the window size."""
        base_size = min(self.width, self.height)
        self.margin_x = round(base_size * 0.055)
        self.margin_y = round(base_size * 0.01)

        self.is_dense_map = len(self.graph.zones) > 31
        zone_ratio = 0.06 if self.is_dense_map else 0.08
        self.zone_size = max(8, round(base_size * zone_ratio))

        self.header_height = round(self.height * 0.07)
        self.footer_height = round(self.height * 0.08)

        self.label_font = pygame.font.Font(
            None, max(12, round(self.height * 0.018))
        )

        label_height = 0
        if not self.is_dense_map:
            label_rows = max(
                len(zone.name.split("_"))
                for zone in self.graph.zones
            )
            label_height = (
                4 + label_rows * self.label_font.get_linesize()
            )

        self.map_left = self.margin_x + self.zone_size / 2
        self.map_top = (
            self.header_height + self.margin_y + self.zone_size / 2
        )
        self.available_width = (
            self.width - (2 * self.margin_x) - self.zone_size
        )
        self.available_height = (
            self.height
            - self.header_height
            - self.footer_height
            - 2 * self.margin_y
            - self.zone_size
            - label_height
        )

    def _init_window_size(self) -> None:
        """Set the window dimensions to 80 percent of the desktop's size."""
        desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
        self.width = int(desktop_width * 0.96)
        self.height = int(desktop_height * 0.9)

    def _init_button(self) -> None:
        """Create previous and next button rectangles in the footer."""
        button_width = round(self.width * 0.12)
        button_height = round(self.footer_height * 0.5)
        gap = round(self.width * 0.02)

        footer_top = self.height - self.footer_height
        button_y = footer_top + (self.footer_height - button_height) // 2
        left = (self.width - 2 * button_width - gap) // 2

        self.previous_button = pygame.Rect(
            left, button_y, button_width, button_height
        )
        self.next_button = pygame.Rect(
            left + button_width + gap, button_y, button_width, button_height
        )

    def _start(self) -> None:
        """Initialize Pygame, display state, font, window, and frame clock."""
        pygame.init()

        self.current_turn = 0
        self._init_window_size()
        self._init_layout()
        self._init_button()
        self._update_positions()
        self._configure_layout()
        self.font = pygame.font.Font(
            None, max(16, round(self.height * 0.03))
        )
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-In")
        self.clock = pygame.time.Clock()

    def _update_positions(self) -> None:
        """
        Reconstruct drone positions at the current turn by replaying
        completed movements from the starting hub.
        """
        self.positions: dict[int, str] = {
            drone.id: self.graph.start_hub.name
            for drone in self.graph.drones
        }

        for turn in self.output[:self.current_turn]:
            for drone_id, location in turn:
                self.positions[drone_id] = location

    def _set_turn(self, turn: int) -> None:
        """
        Select a valid turn and update drone positions.

        Leave the current state unchanged if the turn is out of range.

        Args:
            turn: Number of completed turns, from zero through the total
                number of simulation turns, inclusive.
        """
        if 0 <= turn <= len(self.output):
            self.current_turn = turn
            self._update_positions()

    def _configure_layout(self) -> None:
        """
        Calculate the scale and offsets needed to fit and center the map.

        Scale controls the map's size; offsets control its position. These
        values are used by _to_screen() to convert map coordinates to pixels.
        """
        min_x = min(zone.x for zone in self.graph.zones)
        max_x = max(zone.x for zone in self.graph.zones)
        min_y = min(zone.y for zone in self.graph.zones)
        max_y = max(zone.y for zone in self.graph.zones)
        span_x = max_x - min_x
        span_y = max_y - min_y
        scales = []
        if span_x > 0:
            scales.append(self.available_width / span_x)
        if span_y > 0:
            scales.append(self.available_height / span_y)
        self.scale = (min(scales) if scales else 1.0)
        self.offset_x = (
            self.map_left
            + ((self.available_width - span_x * self.scale) / 2)
            - min_x * self.scale
        )
        self.offset_y = (
            self.map_top
            + ((self.available_height - span_y * self.scale) / 2)
            - min_y * self.scale
        )

    def _to_screen(self, x: float, y: float) -> tuple[int, int]:
        """
        Convert map coordinates to screen pixel coordinates.

        Args:
            x: Horizontal map coordinate.
            y: Vertical map coordinate.

        Returns:
            Rounded screen coordinates as an (x, y) pair.
        """
        screen_x = x * self.scale + self.offset_x
        screen_y = y * self.scale + self.offset_y
        return round(screen_x), round(screen_y)

    def _draw(self) -> None:
        """
        Draw connections, zones, the turn counter, and navigation buttons.
        """
        self.screen.fill(COLORS["white"])
        for connection in self.graph.connections:
            start = self.graph.zone_lookup[connection.from_zone]
            end = self.graph.zone_lookup[connection.to_zone]

            pygame.draw.line(
                self.screen,
                COLORS["gray"],
                self._to_screen(start.x, start.y),
                self._to_screen(end.x, end.y),
                1,
            )

        for zone in self.graph.zones:
            color = (
                COLORS.get(zone.color, COLORS["gray"])
                if zone.color is not None
                else COLORS["gray"]
            )
            position = self._to_screen(zone.x, zone.y)
            zone_rect = pygame.Rect(
                0, 0, self.zone_size, self.zone_size
            )
            zone_rect.center = position
            pygame.draw.rect(
                self.screen, COLORS["white"], zone_rect
            )
            pygame.draw.rect(
                self.screen, color, zone_rect, width=6
            )
        self._draw_drones()
        self._draw_zone_names()
        self._draw_turn_counter()
        self._draw_buttons()

    def _draw_turn_counter(self) -> None:
        """
        Draw the current and total turn counts centered in the header.
        """
        text = self.font.render(
            f"Turn {self.current_turn} / {len(self.output)}",
            True,
            COLORS["black"],
        )
        text_rect = text.get_rect(
            center=(self.width // 2, self.header_height // 2)
        )
        self.screen.blit(text, text_rect)

    def _draw_buttons(self) -> None:
        """Draw the previous and next turn controls in the footer."""
        for rect, label in (
            (self.previous_button, "Previous"),
            (self.next_button, "Next")
        ):
            pygame.draw.rect(self.screen, COLORS["gray"], rect)
            text = self.font.render(label, True, COLORS["white"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def _draw_drones(self) -> None:
        for zone in self.graph.zones:
            drone_ids = [
                drone_id
                for drone_id, location in self.positions.items()
                if location == zone.name
            ]
            if not drone_ids:
                continue

            columns = math.ceil(math.sqrt(len(drone_ids)))
            rows = math.ceil(len(drone_ids) / columns)

            available_size = self.zone_size * 0.8
            cell_size = available_size / columns

            font_size = max(1, int(cell_size * 0.8))
            font = pygame.font.Font(None, font_size)
            longest_label = f"d{max(drone_ids)}"

            while font_size > 1:
                width, height = font.size(longest_label)
                if width <= cell_size * 0.9 and height <= cell_size * 0.9:
                    break
                font_size -= 1
                font = pygame.font.Font(None, font_size)

            center_x, center_y = self._to_screen(zone.x, zone.y)
            left = center_x - columns * cell_size / 2
            top = center_y - rows * cell_size / 2

            for index, drone_id in enumerate(drone_ids):
                column = index % columns
                row = index // columns

                position = (
                    round(left + (column + 0.5) * cell_size),
                    round(top + (row + 0.5) * cell_size),
                )
                text = font.render(
                    f"D{drone_id}", True, COLORS["charcoal"]
                )
                rect = text.get_rect(center=position)
                self.screen.blit(text, rect)

    def _draw_zone_names(self) -> None:
        if self.is_dense_map:
            return

        font = self.label_font

        for zone in self.graph.zones:
            x, y = self._to_screen(zone.x, zone.y)
            y += self.zone_size // 2 + 4

            for word in zone.name.split("_"):
                text = font.render(
                    word, True, COLORS["black"]
                )
                rect = text.get_rect(
                    midtop=(x, y)
                )
                self.screen.blit(text, rect)
                y += font.get_linesize()

    def run(self) -> None:
        """
        Run the interactive visualization until the window is closed.

        Handle navigation button clicks and redraw at up to 60 frames per
        second. Always shut down Pygame when the loop exits or an error occurs.
        """
        try:
            self._start()
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        if self.previous_button.collidepoint(event.pos):
                            self._set_turn(self.current_turn - 1)
                        elif self.next_button.collidepoint(event.pos):
                            self._set_turn(self.current_turn + 1)
                if not running:
                    break
                self._draw()
                pygame.display.flip()
                self.clock.tick(60)
        finally:
            pygame.quit()
