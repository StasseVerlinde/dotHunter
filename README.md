# Dot Hunter

Catch the Dot is a fun, interactive hand‑tracking game built with Python, OpenCV, and MediaPipe. Use your index finger (via webcam) to “catch” a dot that appears randomly on screen.

## Prerequisites
- Python installed
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
Run the game with:
```bash
python demo.py
```
- A window will open showing your webcam feed with a red dot.
- Move your index finger to touch the dot—when the dot is caught, your score increases and a new dot appears.
- Press **q** or **Esc** to exit the game.