import cv2
import random
import math
import os


def load_image_with_alpha(image_path, size=(60, 60)):
    """
    Load an image with alpha channel and resize it.
    
    Args:
        image_path (str): Path to the image file.
        size (tuple): Target size (width, height).
    
    Returns:
        np.ndarray: Image with alpha channel (BGRA format).
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")
    
    # Resize with high-quality interpolation
    img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    
    # Ensure image has alpha channel
    if img.shape[2] == 3:
        # Add alpha channel if missing
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    return img


class GameObject:
    """
    Represents a collectible object (coin or bomb) in the game.
    
    Attributes:
        x (int): X-coordinate of the object center.
        y (int): Y-coordinate of the object center.
        obj_type (str): Type of object ('coin' or 'bomb').
        image (np.ndarray): Image data with alpha channel.
        width (int): Width of the object.
        height (int): Height of the object.
        radius (int): Collision radius (approximate).
    """
    
    def __init__(self, x, y, obj_type, image):
        """
        Initialize a game object.
        
        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.
            obj_type (str): 'coin' or 'bomb'.
            image (np.ndarray): Image data with alpha channel.
        """
        self.x = x
        self.y = y
        self.obj_type = obj_type
        self.image = image
        self.height, self.width = image.shape[:2]
        self.radius = min(self.width, self.height) // 2
    
    def draw(self, frame):
        """
        Draw the object on the frame with alpha blending.
        
        Args:
            frame (np.ndarray): The frame to draw on (BGR format).
        """
        # Calculate top-left corner position
        x1 = self.x - self.width // 2
        y1 = self.y - self.height // 2
        x2 = x1 + self.width
        y2 = y1 + self.height
        
        # Ensure object is within frame bounds
        if x1 < 0 or y1 < 0 or x2 > frame.shape[1] or y2 > frame.shape[0]:
            return
        
        # Extract alpha channel and create mask
        if self.image.shape[2] == 4:
            alpha = self.image[:, :, 3] / 255.0
            # Overlay RGB channels with alpha blending
            for c in range(3):
                frame[y1:y2, x1:x2, c] = (
                    alpha * self.image[:, :, c] +
                    (1 - alpha) * frame[y1:y2, x1:x2, c]
                )
        else:
            # No alpha channel, just overlay directly
            frame[y1:y2, x1:x2] = self.image[:, :, :3]
    
    def check_collision(self, finger_x, finger_y):
        """
        Check if a finger position collides with this object.
        
        Args:
            finger_x (int or None): X-coordinate of finger.
            finger_y (int or None): Y-coordinate of finger.
        
        Returns:
            bool: True if collision detected.
        """
        if finger_x is None or finger_y is None:
            return False
        
        distance = math.hypot(finger_x - self.x, finger_y - self.y)
        return distance < self.radius


class CollectibleGame:
    """
    CollectibleGame manages coins and bombs that players can collect.
    
    Attributes:
        frame_width (int): Width of the frame/canvas.
        frame_height (int): Height of the frame/canvas.
        players (int): Number of players.
        scores (List[int]): Scores for each player.
        objects (List[GameObject]): Active game objects on screen.
        coin_image (np.ndarray): Loaded coin image.
        bomb_image (np.ndarray): Loaded bomb image.
        max_coins (int): Maximum number of coins on screen.
        max_bombs (int): Maximum number of bombs on screen.
    """
    
    def __init__(self, frame_width, frame_height, players=1, max_coins=3, max_bombs=2):
        """
        Initialize the game state and load assets.
        
        Args:
            frame_width (int): Width of game area.
            frame_height (int): Height of game area.
            players (int): Number of players.
            max_coins (int): Maximum coins on screen.
            max_bombs (int): Maximum bombs on screen.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.players = players
        self.scores = [0] * players
        self.max_coins = max_coins
        self.max_bombs = max_bombs
        self.objects = []
        
        # Load game assets
        # Get path to assets folder (parent directory of src)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(current_dir), "assets")
        
        coin_path = os.path.join(assets_dir, "vecteezy_game-coin-pixelated_54978935.png")
        bomb_path = os.path.join(assets_dir, "vecteezy_game-item-pixelated-bomb_57467426.png")
        
        self.coin_image = load_image_with_alpha(coin_path, size=(60, 60))
        self.bomb_image = load_image_with_alpha(bomb_path, size=(60, 60))
        
        # Spawn initial objects
        self._spawn_initial_objects()
    
    def _spawn_initial_objects(self):
        """Spawn initial random objects on the screen."""
        # Spawn 3-5 coins (higher spawn rate)
        num_coins = random.randint(max(3, self.max_coins - 2), self.max_coins)
        for _ in range(num_coins):
            self._spawn_object('coin')
        
        # Spawn 0-1 bombs (lower spawn rate)
        num_bombs = random.randint(0, min(1, self.max_bombs))
        for _ in range(num_bombs):
            self._spawn_object('bomb')
    
    def _spawn_object(self, obj_type):
        """
        Spawn a new object of the specified type at a random position.
        
        Args:
            obj_type (str): 'coin' or 'bomb'.
        """
        padding = 80
        x = random.randint(padding, self.frame_width - padding)
        y = random.randint(padding, self.frame_height - padding)
        
        image = self.coin_image if obj_type == 'coin' else self.bomb_image
        obj = GameObject(x, y, obj_type, image)
        self.objects.append(obj)
    
    def _count_objects(self, obj_type):
        """
        Count how many objects of a given type are active.
        
        Args:
            obj_type (str): 'coin' or 'bomb'.
        
        Returns:
            int: Count of objects.
        """
        return sum(1 for obj in self.objects if obj.obj_type == obj_type)
    
    def draw_objects(self, frame):
        """
        Draw all active objects on the frame.
        
        Args:
            frame (np.ndarray): The frame to draw on.
        """
        for obj in self.objects:
            obj.draw(frame)
    
    def check_collisions(self, finger_positions: list[tuple[int | None, int | None]]):
        """
        Check all fingertips against all objects for collisions.
        Update scores and respawn objects as needed.
        
        Args:
            finger_positions (List[Tuple[int|None, int|None]]):
                A list of (x, y) coordinates for each player's index fingertip,
                or (None, None) if that hand wasn't detected.
        """
        objects_to_remove = []
        
        for i, (fx, fy) in enumerate(finger_positions):
            if fx is None or fy is None:
                continue
            
            for obj in self.objects:
                if obj.check_collision(fx, fy):
                    # Update score based on object type
                    if obj.obj_type == 'coin':
                        self.scores[i] += 1
                    elif obj.obj_type == 'bomb':
                        self.scores[i] -= 3
                    
                    # Mark object for removal
                    if obj not in objects_to_remove:
                        objects_to_remove.append(obj)
                    
                    # Only one object per finger per frame
                    break
        
        # Remove caught objects and spawn new ones
        for obj in objects_to_remove:
            self.objects.remove(obj)
            self._respawn_object()
    
    def _respawn_object(self):
        """
        Spawn a new random object, respecting maximum counts.
        Favors coins over bombs (80% coin, 20% bomb when both available).
        """
        coin_count = self._count_objects('coin')
        bomb_count = self._count_objects('bomb')
        
        # Determine what can be spawned
        can_spawn_coin = coin_count < self.max_coins
        can_spawn_bomb = bomb_count < self.max_bombs
        
        if not can_spawn_coin and not can_spawn_bomb:
            return  # Both at max, don't spawn
        
        # Choose randomly among available options, favoring coins
        if can_spawn_coin and can_spawn_bomb:
            # 80% chance of coin, 20% chance of bomb
            obj_type = random.choices(['coin', 'bomb'], weights=[80, 20])[0]
        elif can_spawn_coin:
            obj_type = 'coin'
        else:
            obj_type = 'bomb'
        
        self._spawn_object(obj_type)


# Keep DotGame for backward compatibility (though it won't be used)
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

    def check_collisions(self, finger_positions: list[tuple[int | None, int | None]]):
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
