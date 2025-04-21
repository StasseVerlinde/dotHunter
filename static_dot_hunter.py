"""
static_dot_hunter.py

Static‑image checker: overlays a randomly placed dot onto the input image,
then prints & visualizes whether the index‑finger tip touches that dot.

Usage:
    python static_dot_hunter.py --image path/to/hand_image.png
"""

import cv2
import argparse
import math
from src.hand_tracker import HandTracker
from src.dot_game import DotGame


def main():
    parser = argparse.ArgumentParser(
        description="Overlay a random dot on a static hand image, "
        "then check if the index fingertip touches it."
    )
    parser.add_argument(
        "--image", "-i", required=True, help="Path to the input image containing a hand"
    )

    parser.add_argument(
        "--force-detection",
        "-f",
        required=False,
        action="store_true",
        help="Force the dot to appear on your index-finger tip rather than at a random spot",
    )

    args = parser.parse_args()

    # 1) Load image
    image = cv2.imread(args.image)
    if image is None:
        print(f"Error: could not read image '{args.image}'")
        return

    height, width = image.shape[:2]

    # 2) Detect the index-finger tip in static mode
    tracker = HandTracker(
        mode=True, maxHands=1, detectionCon=0.7, trackCon=0.7  # static image mode
    )
    _ = tracker.find_hands(image, draw=False)
    fx, fy = tracker.get_index_finger_tip(image)
    if fx is None or fy is None:
        print("No hand (or index finger) detected in the image.")
        return
    
    if not args.force_detection:
        # 3) Spawn a random dot using your DotGame logic
        game = DotGame(frame_width=width, frame_height=height, dot_radius=20, players=1)
    else:
        # 3) Spawn a dot at the fingertip position
        game = DotGame(frame_width=width, frame_height=height, dot_radius=20, players=1)
        game.dot_x = fx
        game.dot_y = fy
        game.dot_radius = 20

    # 4) Draw dot + fingertip onto a copy of the image
    out = image.copy()
    game.draw_dot(out)  # draw the red dot
    cv2.circle(
        out, (fx, fy), 8, (255, 0, 0), -1
    )  # draw the detected fingertip as a blue dot

    # 5) Compute distance & decide “touch”
    dist = math.hypot(fx - game.dot_x, fy - game.dot_y)
    touching = dist <= game.dot_radius

    # 6) Print results
    print(f"Dot center:    ({game.dot_x}, {game.dot_y}), radius = {game.dot_radius}")
    print(f"Index fingertip: ({fx}, {fy}), distance = {dist:.1f}")
    print("Touching dot? ->", touching)

    # 7) Annotate result text
    label = "TOUCHING" if touching else "NOT TOUCHING"
    cv2.putText(out, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    # 8) Show window
    window_name = "Static Dot Hunter"
    cv2.imshow(window_name, out)

    # wait until user presses Esc/Q or closes the window
    while True:
        key = cv2.waitKey(100) & 0xFF
        # exit on Esc or 'q'
        if key == 27 or key == ord("q"):
            break
        # exit if window was closed manually
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
