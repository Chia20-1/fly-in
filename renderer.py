from simulation import SimulationOutput
from models import Graph
import pygame


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
}


class TextOutput:
    """
    """
    def __init__(self, output: SimulationOutput) -> None:
        """
        """
        self.output = output

    def print_output(self) -> None:
        for turn in self.output:
            for movement in turn:
                drone_id, destination = movement
                print(f"D{drone_id}-{destination}", end=" ")
            print()
        print(f"Turns: {len(self.output)}")


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

    def _init_display_state(self) -> None:
        """
        """
        self.current_turn = 0
        self._init_window_size()
        base_size = min(self.width, self.height)
        self.margin = round(base_size * 0.055)
        self.radius = max(1, round(base_size * 0.0175))
        self.header_height = round(self.height * 0.28)
        self.footer_height = round(self.height * 0.125)
        self.available_width = self.width - (2 * self.margin)
        self.available_height = (
            self.height
            - self.header_height
            - self.footer_height
            - 2 * self.margin
        )
        self._init_button()
        self._update_positions()

    def _init_window_size(self) -> None:
        """
        """
        desktop_width, desktop_height = pygame.display.get_desktop_sizes()[0]
        self.width = int(desktop_width * 0.8)
        self.height = int(desktop_height * 0.8)

    def _init_button(self) -> None:
        """
        """
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
        """
        """
        pygame.init()
        self._init_display_state()
        self.font = pygame.font.Font(
            None, max(16, round(self.height * 0.03))
        )
        self.screen = pygame.display.set_mode((self.width, self.height))
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
        self.scale = min(scales) if scales else 1.0
        self.offset_x = (
            self.margin
            + ((self.available_width - span_x * self.scale) / 2)
            - min_x * self.scale
        )
        self.offset_y = (
            self.header_height
            + self.margin
            + ((self.available_height - span_y * self.scale) / 2)
            - min_y * self.scale
        )

    def _to_screen(self, x: float, y: float) -> tuple[int, int]:
        """
        """
        screen_x = x * self.scale + self.offset_x
        screen_y = y * self.scale + self.offset_y
        return round(screen_x), round(screen_y)

    def _draw(self) -> None:
        """
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
                2,
            )

        occupied_locations = set(self.positions.values())
        for zone in self.graph.zones:
            color = (
                COLORS.get(zone.color, COLORS["gray"])
                if zone.color is not None
                else COLORS["gray"]
            )
            position = self._to_screen(zone.x, zone.y)
            is_occupied = zone.name in occupied_locations
            fill_color = color if is_occupied else COLORS["white"]
            pygame.draw.circle(
                self.screen, fill_color, position, self.radius
            )
            pygame.draw.circle(
                self.screen, color, position, self.radius, width=6
            )

        self._draw_movements()
        self._draw_buttons()

    def _draw_movements(self) -> None:
        """Draw the turn number nad its movements in header columns"""
        padding = max(4, round(self.height * 0.01))
        row_height = self.font.get_linesize()
        heading = self.font.render(
            f"Turn {self.current_turn} / {len(self.output)}",
            True,
            COLORS["black"],
        )
        self.screen.blit(heading, (self.margin, padding))

        messages = self._get_movement_messages()
        if not messages:
            return

        # Calculate how many rows fit beneath the heading.
        text_top = padding + row_height + padding
        rows, columns, column_width = self._get_movement_layout(
            messages, text_top, padding
        )
        if rows < 1:
            return

        capacity = rows * columns
        if len(messages) > capacity:
            hidden_count = len(messages) - capacity + 1
            messages = messages[:capacity - 1]
            messages.append(f"+ {hidden_count} more movements")

        self._draw_movement_messages(
            messages, text_top, rows, column_width
        )

    def _get_movement_messages(self) -> list[str]:
        """
        """
        if self.current_turn == 0:
            return []

        return [
            f"Drone {drone_id} moved to {destination}"
            for drone_id, destination
            in self.output[self.current_turn - 1]
        ]

    def _get_movement_layout(
        self,
        messages: list[str],
        text_top: int,
        padding: int,
    ) -> tuple[int, int, int]:
        """
        """
        available_height = self.header_height - text_top - padding
        rows = max(0, available_height // self.font.get_linesize())
        if rows < 1:
            return 0, 0, 0
        needed_columns = (len(messages) + rows - 1) // rows
        columns = min(3, needed_columns)
        column_width = self.available_width // columns
        return rows, columns, column_width

    def _fit_text(self, message: str, max_width: int) -> str:
        """
        """
        if self.font.size(message)[0] <= max_width:
            return message

        suffix = "..."
        if self.font.size(suffix)[0] > max_width:
            return ""

        while message and self.font.size(message + suffix)[0] > max_width:
            message = message[:-1]

        return message + suffix

    def _draw_movement_messages(
        self,
        messages: list[str],
        text_top: int,
        rows: int,
        column_width: int,
    ) -> None:
        """
        """
        row_height = self.font.get_linesize()
        gap = max(8, round(self.width * 0.02))
        text_width = max(1, column_width - gap)

        for index, message in enumerate(messages):
            column = index // rows
            row = index % rows
            x = self.margin + column * column_width
            y = text_top + row * row_height
            message = self._fit_text(message, text_width)
            text = self.font.render(message, True, COLORS["black"])
            self.screen.blit(text, (x, y))

    def _draw_buttons(self) -> None:
        """Draw the previous and next turn controls"""
        for rect, label in (
            (self.previous_button, "Previous"),
            (self.next_button, "Next")
        ):
            pygame.draw.rect(self.screen, COLORS["gray"], rect)
            text = self.font.render(label, True, COLORS["white"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def run(self) -> None:
        """
        """
        try:
            self._start()
            self._configure_layout()
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
