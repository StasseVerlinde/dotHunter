import cv2
import random
import math


class DotGame:
    def __init__(self, frame_width, frame_height, dot_radius=20, players=1):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.dot_radius = dot_radius
        self.players = players
        self.scores = [0] * players
        self.spawn_dot()

    def spawn_dot(self):
        self.dot_x = random.randint(self.dot_radius, self.frame_width - self.dot_radius)
        self.dot_y = random.randint(
            self.dot_radius, self.frame_height - self.dot_radius
        )

    def draw_dot(self, frame):
        cv2.circle(frame, (self.dot_x, self.dot_y), self.dot_radius, (0, 0, 255), -1)

    def check_collisions(self, finger_positions):
        """
        finger_positions: list of (x,y) for each player.
        Increments the first player's score whose finger hits the dot, then respawns it.
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
    print("Please run demo.py to start the game.")
