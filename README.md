# Dot Hunter

Dot Hunter is a fun, interactive hand‑tracking game built with Python, OpenCV, and MediaPipe. Use your index finger (via webcam) to “catch” a dot that appears randomly on the screen.

## Prerequisites
- Python
- tkinter
  - For Windows, it is included with Python by default.
  - For Linux, you can install it using:
    ```bash
    sudo apt-get install python3-tk
    ```
  - For Mac, you can install it using:
    ```bash
    brew install python-tk
    ```

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Real-Time Game
Run the real-time game with:
```bash
python streaming_dot_hunter.py
```
- A settings window will appear where you can select the screen resolution and game mode (Solo or Two Players).
- A webcam window will open showing your feed with a red dot.
- Move your index finger to touch the dot—when the dot is caught, your score increases, and a new dot appears.
- Press **q** or **Esc** to exit the game.

### Static Image Checker
Test the game logic on a static image with:
```bash
python static_dot_hunter.py --image path/to/hand_image.png
```
or you can use the image in the *img* folder:
```bash 
python static_dot_hunter.py --image ./img/pointingHand_demo.jpg
```
- A random dot will be overlaid on the image, and the program will check if your index finger touches the dot.
- Use the `--force-detection` flag to place the dot directly on your fingertip.


## Project Folder Structure
The project is organized as follows:

```
dotHunter/
├── streaming_dot_hunter.py   # Main script for the real-time game
├── static_dot_hunter.py      # Main script for the static game
├── src/                      # Source folder containing core modules
│   ├── hand_tracker.py       # Hand tracking logic using MediaPipe
│   ├── dot_game.py           # Game logic for dot placement and scoring
├── README.md                 # Project documentation
├── instruction.md            # Instructions for the coding challenge
├── requirements.txt          # Python dependencies
```