import cv2
import random
import math


class DotGame:
    """
    DotGame manages a simple “catch the dot” mechanic on a 2D frame.

    Attributes:
        frame_width (int): Width of the frame/canvas.
        frame_height (int): Height of the frame/canvas.
        dot_radius (int): Radius of the red dot.
        players (int): Number of players (i.e. number of fingertips to track).
        scores (List[int]): Scores for each player.
        dot_x (int), dot_y (int): Current center coordinates of the dot.
    """

    def __init__(self, frame_width, frame_height, dot_radius=20, players=1):
        """
        Initialize the game state, allocate score counters, and spawn the first dot.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.dot_radius = dot_radius
        self.players = players
        self.scores = [0] * players
        self.spawn_dot()

    def spawn_dot(self):
        """
        Choose a new random (x, y) for the dot within the frame bounds,
        leaving a padding so it never appears too close to the edges.
        """
        padding = 50
        self.dot_x = random.randint(
            self.dot_radius + padding, self.frame_width - self.dot_radius - padding
        )
        self.dot_y = random.randint(
            self.dot_radius + padding, self.frame_height - self.dot_radius - padding
        )

    def draw_dot(self, frame):
        """
        Draw the red dot onto the given frame at (dot_x, dot_y).

        Args:
            frame (np.ndarray): The image on which to draw.
        """
        cv2.circle(frame, (self.dot_x, self.dot_y), self.dot_radius, (0, 0, 255), -1)

    def check_collisions(self, finger_positions):
        """
        Check each player's fingertip for collision with the dot.
        If the fingertip lies within the dot's radius, increment that
        player's score, respawn the dot, and stop checking further players.

        Args:
            finger_positions (List[Tuple[int|None, int|None]]):
                A list of (x, y) coordinates for each player's index fingertip,
                or (None, None) if that hand wasn't detected.
        """
        for i, (x, y) in enumerate(finger_positions):
            if x is None or y is None:
                continue
            if math.hypot(x - self.dot_x, y - self.dot_y) < self.dot_radius:
                self.scores[i] += 1
                self.spawn_dot()
                break


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    exit(1)
