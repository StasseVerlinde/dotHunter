import cv2
import random
import math

class DotGame:
    """
    DotGame manages the dot's position, rendering, and collision detection.
    """
    def __init__(self, frame_width, frame_height, dot_radius=20):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.dot_radius = dot_radius
        self.score = 0
        self.spawn_dot()

    def spawn_dot(self):
        """
        Randomly positions the dot ensuring it's fully inside the frame.
        """
        self.dot_x = random.randint(self.dot_radius, self.frame_width - self.dot_radius)
        self.dot_y = random.randint(self.dot_radius, self.frame_height - self.dot_radius)

    def draw_dot(self, frame):
        """
        Draws the dot on the given frame.
        """
        cv2.circle(frame, (self.dot_x, self.dot_y), self.dot_radius, (0, 0, 255), -1)

    def check_collision(self, finger_x, finger_y):
        """
        Checks if the finger (x, y) collides with the dot.
        If collision occurs, increments score and respawns dot.
        Returns True if collided, False otherwise.
        """
        if finger_x is None or finger_y is None:
            return False
        dx = finger_x - self.dot_x
        dy = finger_y - self.dot_y
        distance = math.hypot(dx, dy)
        if distance < self.dot_radius:
            self.score += 1
            self.spawn_dot()
            return True
        return False