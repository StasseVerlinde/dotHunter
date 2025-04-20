import cv2
from hand_tracker import HandTracker
from dot_game import DotGame

def main():
    # Initialize webcam feed
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize the hand tracker and game logic
    tracker = HandTracker(mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7)
    game = DotGame(frame_width, frame_height, dot_radius=20)

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Could not read frame from webcam.")
            break
        frame = cv2.flip(frame, 1) # Flip frame horizontally

        # Detect hands and get fingertip coordinates
        frame = tracker.find_hands(frame, draw=False)
        finger_x, finger_y = tracker.get_index_finger_tip(frame)

        # Track finger position
        if finger_x is not None and finger_y is not None:
            cv2.circle(frame, (finger_x, finger_y), 5, (255, 0, 0), -1)

        # Draw the target dot and check for collision
        game.draw_dot(frame)
        game.check_collision(finger_x, finger_y)

        # Display the score
        cv2.putText(frame, f"Score: {game.score}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.imshow("Dot Hunter", frame)
        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
