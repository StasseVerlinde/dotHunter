"""
streaming_dot_hunter.py

Real‑time “catch the dot” game using your webcam and MediaPipe.
Run with: python streaming_dot_hunter.py
"""

import cv2
import time
import json
import os
import tkinter as tk
from tkinter import ttk
from src.hand_tracker import HandTracker
from src.dot_game import CollectibleGame


HIGHSCORE_FILE = "highscores.json"


def load_highscores():
    """Load high scores from JSON file."""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_highscores(highscores):
    """Save high scores to JSON file."""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            json.dump(highscores, f, indent=2)
    except IOError as e:
        print(f"Error saving high scores: {e}")


def add_highscore(name, score, players):
    """Add a new high score and return updated list (top 10)."""
    mode = "Solo" if players == 1 else "Two Players"
    highscores = load_highscores()
    
    # Always add score entry (allow duplicates and all scores)
    highscores.append({
        "name": name,
        "score": score,
        "mode": mode,
        "date": time.strftime("%Y-%m-%d %H:%M")
    })
    
    # Sort by score (descending) and keep top 10
    highscores.sort(key=lambda x: x['score'], reverse=True)
    highscores = highscores[:10]
    save_highscores(highscores)
    return highscores


def show_game_over_screen(final_scores, players, timer_duration):
    """Show game over screen and get player name(s), return play_again boolean."""
    root = tk.Tk()
    root.title("Game Over!")
    root.resizable(False, False)
    
    player_names = []
    
    # Title
    ttk.Label(root, text="Game Over!", font=('Arial', 20, 'bold')).grid(
        row=0, column=0, columnspan=2, pady=(20, 10)
    )
    
    # Show scores and get names
    name_entries = []
    if players == 1:
        ttk.Label(root, text=f"Final Score: {final_scores[0]}", font=('Arial', 14)).grid(
            row=1, column=0, columnspan=2, pady=5
        )
        ttk.Label(root, text="Enter your name:").grid(row=2, column=0, columnspan=2, pady=(10, 0))
        name_entry = ttk.Entry(root, width=25)
        name_entry.grid(row=3, column=0, columnspan=2, padx=20, pady=5)
        name_entry.focus()
        name_entries.append(name_entry)
    else:
        ttk.Label(root, text=f"Player 1 Score: {final_scores[0]}", font=('Arial', 12)).grid(
            row=1, column=0, columnspan=2, pady=5
        )
        ttk.Label(root, text="Player 1 Name:").grid(row=2, column=0, sticky="e", padx=(20, 5))
        p1_entry = ttk.Entry(root, width=20)
        p1_entry.grid(row=2, column=1, sticky="w", padx=(5, 20), pady=5)
        p1_entry.focus()
        name_entries.append(p1_entry)
        
        ttk.Label(root, text=f"Player 2 Score: {final_scores[1]}", font=('Arial', 12)).grid(
            row=3, column=0, columnspan=2, pady=5
        )
        ttk.Label(root, text="Player 2 Name:").grid(row=4, column=0, sticky="e", padx=(20, 5))
        p2_entry = ttk.Entry(root, width=20)
        p2_entry.grid(row=4, column=1, sticky="w", padx=(5, 20), pady=5)
        name_entries.append(p2_entry)
    
    # High scores display
    ttk.Label(root, text="High Scores", font=('Arial', 14, 'bold')).grid(
        row=5 if players == 1 else 5, column=0, columnspan=2, pady=(20, 5)
    )
    
    highscores = load_highscores()
    scores_text = tk.Text(root, height=8, width=50, state='disabled', font=('Courier', 10))
    scores_text.grid(row=6 if players == 1 else 6, column=0, columnspan=2, padx=20, pady=5)
    
    scores_text.config(state='normal')
    if highscores:
        for i, hs in enumerate(highscores[:10], 1):
            line = f"{i:2}. {hs['name']:<20} {hs['score']:>5} pts  [{hs['mode']}]\n"
            scores_text.insert('end', line)
    else:
        scores_text.insert('end', "No high scores yet. Be the first!")
    scores_text.config(state='disabled')
    
    def on_submit():
        # Get names and save high scores only if name is provided
        for i, entry in enumerate(name_entries):
            name = entry.get().strip()
            if name:  # Only add to high scores if name is not empty
                player_names.append(name)
                add_highscore(name, final_scores[i], players)
        
        root.destroy()
    
    # Buttons (only Quit)
    button_frame = ttk.Frame(root)
    button_frame.grid(row=7 if players == 1 else 7, column=0, columnspan=2, pady=(15, 20))
    ttk.Button(button_frame, text="Quit", command=on_submit).pack(side='left', padx=5)

    # Handle Enter key (just submit and quit)
    def on_enter(event):
        on_submit()

    root.bind('<Return>', on_enter)
    root.protocol("WM_DELETE_WINDOW", on_submit)

    root.mainloop()

    return False


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
    ttk.Label(root, text="Select mode:").grid(
        row=0, column=0, columnspan=2, pady=(10, 0)
    )
    mode_var = tk.StringVar(value="Solo")
    ttk.Radiobutton(root, text="Solo", variable=mode_var, value="Solo").grid(
        row=1, column=0, padx=20, sticky="w"
    )
    ttk.Radiobutton(root, text="Two Players", variable=mode_var, value="Two").grid(
        row=1, column=1, padx=20, sticky="w"
    )

    # Timer duration
    ttk.Label(root, text="Timer duration (seconds):").grid(
        row=2, column=0, columnspan=2, pady=(10, 0)
    )
    timer_var = tk.IntVar(value=60)
    timer_spinbox = ttk.Spinbox(
        root, from_=10, to=300, increment=10, textvariable=timer_var, width=10
    )
    timer_spinbox.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    ttk.Button(root, text="Start Game", command=on_start).grid(
        row=4, column=0, columnspan=2, pady=(15, 10)
    )

    root.mainloop()

    # if they closed without clicking Start, abort
    if cancelled["value"]:
        return None, None

    return (
        (1 if mode_var.get() == "Solo" else 2),
        timer_var.get(),
    )


def run_game_session(settings):
    """Run a single game session with the given settings."""
    players, timer_duration = settings

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return False
    
    # Get screen resolution for fullscreen mode
    temp_root = tk.Tk()
    screen_width = temp_root.winfo_screenwidth()
    screen_height = temp_root.winfo_screenheight()
    temp_root.destroy()
    
    # Set webcam to a standard resolution for optimal hand tracking
    # Use 1280x720 as a good balance between quality and performance
    webcam_width, webcam_height = 1280, 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, webcam_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, webcam_height)

    # Create fullscreen window without decorations
    # Use unique window name to ensure fresh window creation on replay
    window_name = f"Dot Hunter {int(time.time() * 1000)}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Allow window to initialize before setting fullscreen
    cv2.waitKey(1)
    
    # Set fullscreen property
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    tracker = HandTracker(mode=False, maxHands=players, detectionCon=0.7, trackCon=0.7)
    game = CollectibleGame(screen_width, screen_height, players=players, max_coins=5, max_bombs=1)
    
    # Calculate scaling factors for hand tracking
    scale_x = screen_width / webcam_width
    scale_y = screen_height / webcam_height
    
    # Start timer (countdown)
    start_time = time.time()
    game_over = False

    while not game_over:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break
        frame = cv2.flip(frame, 1)

        # detect hands on original frame
        frame = tracker.find_hands(frame, draw=False)

        # get fingertip(s) from original frame
        if players == 2:
            by_hand = tracker.get_index_finger_tips_by_handedness(frame)
            tips = [
                by_hand.get("Left", (None, None)),
                by_hand.get("Right", (None, None)),
            ]
        else:
            x, y = tracker.get_index_finger_tip(frame)
            tips = [(x, y)]
        
        # Resize frame to screen dimensions (stretch to fill entire screen)
        frame = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_LINEAR)
        
        # Scale finger positions to match resized frame
        scaled_tips = []
        for x, y in tips:
            if x is not None and y is not None:
                scaled_tips.append((int(x * scale_x), int(y * scale_y)))
            else:
                scaled_tips.append((None, None))
        tips = scaled_tips

        # draw each fingertip
        colors = [(255, 0, 0), (0, 255, 0)]
        for i, (x, y) in enumerate(tips):
            if x is not None and y is not None:
                cv2.circle(frame, (x, y), 7, colors[i], -1)

        # game logic
        game.draw_objects(frame)
        game.check_collisions(tips)
        
        # Calculate remaining time (countdown)
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, timer_duration - elapsed_time)
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        
        # Check if time is up
        if remaining_time == 0:
            game_over = True
        
        # Get text size for centering
        (text_width, _), _ = cv2.getTextSize(
            timer_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2
        )
        timer_x = (frame.shape[1] - text_width) // 2
        
        # Draw timer with background for visibility (red when low)
        timer_bg_color = (0, 0, 255) if remaining_time <= 10 else (0, 0, 0)
        cv2.rectangle(
            frame,
            (timer_x - 10, 5),
            (timer_x + text_width + 10, 40),
            timer_bg_color,
            -1
        )
        cv2.putText(
            frame,
            timer_text,
            (timer_x, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )

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
            
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:  # ESC or 'q' to quit
            break

        # Stop the game if the window is closed
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cap.release()
    cv2.destroyWindow(window_name)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    
    # Show game over screen (no play again option)
    if game_over or elapsed_time >= timer_duration - 1:  # Only show if game completed
        show_game_over_screen(game.scores, players, timer_duration)
        return False

    return False  # Don't play again if quit early


def main():
    """Main entry point - handles play again loop."""
    settings = get_user_settings()
    if settings is None or settings[0] is None:
        print("Settings canceled. Exiting.")
        return

    run_game_session(settings)


if __name__ == "__main__":
    main()
