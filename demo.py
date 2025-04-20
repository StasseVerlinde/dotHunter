import cv2
import tkinter as tk
from tkinter import ttk
from hand_tracker import HandTracker
from dot_game import DotGame


def get_user_settings():
    root = tk.Tk()
    root.title("Dot Hunter — Settings")
    root.resizable(False, False)

    # this dict lets us detect if Start Game was clicked
    cancelled = {"value": True}

    def on_start():
        cancelled["value"] = False
        root.destroy()

    # if they click the window X, just destroy (cancelled stays True)
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # ——— Layout —
    ttk.Label(root, text="Select screen size:").grid(
        row=0, column=0, columnspan=2, pady=(10, 0)
    )
    resolutions = {
        "640×480": (640, 480),
        "800×600": (800, 600),
        "1024×768": (1024, 768),
    }
    res_var = tk.StringVar(value="640×480")
    ttk.OptionMenu(root, res_var, res_var.get(), *resolutions.keys()).grid(
        row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew"
    )

    ttk.Label(root, text="Select mode:").grid(
        row=2, column=0, columnspan=2, pady=(10, 0)
    )
    mode_var = tk.StringVar(value="Solo")
    ttk.Radiobutton(root, text="Solo", variable=mode_var, value="Solo").grid(
        row=3, column=0, padx=20, sticky="w"
    )
    ttk.Radiobutton(root, text="Two Players", variable=mode_var, value="Two").grid(
        row=3, column=1, padx=20, sticky="w"
    )

    ttk.Button(root, text="Start Game", command=on_start).grid(
        row=4, column=0, columnspan=2, pady=(15, 10)
    )

    root.mainloop()

    # if they closed without clicking Start, abort
    if cancelled["value"]:
        return None, None

    return resolutions[res_var.get()], (1 if mode_var.get() == "Solo" else 2)


def main():
    settings = get_user_settings()
    if settings[0] is None:
        print("Settings canceled. Exiting.")
        return

    (width, height), players = settings

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    tracker = HandTracker(mode=False, maxHands=players, detectionCon=0.7, trackCon=0.7)
    game = DotGame(width, height, dot_radius=20, players=players)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break
        frame = cv2.flip(frame, 1)

        # detect hands
        frame = tracker.find_hands(frame, draw=False)

        # get fingertip(s)
        if players == 2:
            by_hand = tracker.get_index_finger_tips_by_handedness(frame)
            tips = [
                by_hand.get("Left", (None, None)),
                by_hand.get("Right", (None, None)),
            ]
        else:
            x, y = tracker.get_index_finger_tip(frame)
            tips = [(x, y)]

        # draw each fingertip
        colors = [(255, 0, 0), (0, 255, 0)]
        for i, (x, y) in enumerate(tips):
            if x is not None and y is not None:
                cv2.circle(frame, (x, y), 7, colors[i], -1)

        # game logic
        game.draw_dot(frame)
        game.check_collisions(tips)

        # draw scores
        if players == 1:
            cv2.putText(
                frame,
                f"Score: {game.scores[0]}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )
        else:
            cv2.putText(
                frame,
                f"P1: {game.scores[0]}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                colors[0],
                2,
            )
            cv2.putText(
                frame,
                f"P2: {game.scores[1]}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                colors[1],
                2,
            )

        cv2.imshow("Dot Hunter", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:  # ESC or 'q' to quit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
