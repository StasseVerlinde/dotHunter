import cv2
import mediapipe as mp


class HandTracker:
    """
    HandTracker wraps MediaPipe Hands to detect hand landmarks and extract
    index-finger tip positions.

    Attributes:
        mode (bool): If True, runs in static_image_mode (no temporal smoothing).
        maxHands (int): Maximum number of hands to detect.
        detectionCon (float): Minimum confidence for initial detection.
        trackCon (float): Minimum confidence for tracking landmarks.
        hands: The MediaPipe Hands object.
        mpDraw: Utility for drawing landmarks & connections.
        results: Storage for the latest detection results.
    """

    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):
        """
        Configure the MediaPipe Hands solution.
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon,
        )
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, frame, draw=True):
        """
        Process an image to detect hand landmarks.

        Args:
            frame (np.ndarray): BGR image from OpenCV.
            draw (bool): Whether to overlay the landmark skeletons on the image.

        Returns:
            np.ndarray: The annotated frame (if draw=True) or original frame.
        """
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks and draw:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(
                    frame, handLms, self.mpHands.HAND_CONNECTIONS
                )
        return frame

    def get_index_finger_tip(self, frame):
        """
        Get the (x, y) pixel coordinates of the first detected index-finger tip.

        Args:
            frame (np.ndarray): Used to obtain image dimensions.

        Returns:
            (int, int) or (None, None): Coordinates of the tip, or None if no hand.
        """
        h, w = frame.shape[:2]
        if self.results.multi_hand_landmarks:
            lm = self.results.multi_hand_landmarks[0].landmark[
                self.mpHands.HandLandmark.INDEX_FINGER_TIP
            ]
            return int(lm.x * w), int(lm.y * h)
        return None, None

    def get_index_finger_tips_by_handedness(self, frame):
        """
        Get a mapping of handedness ("Left"/"Right") to index-finger tip coords.

        Args:
            frame (np.ndarray): Used to obtain image dimensions.

        Returns:
            dict: {"Left": (x, y), "Right": (x, y)}, keys only for detected hands.
        """
        tips = {}
        h, w = frame.shape[:2]
        if not (self.results.multi_hand_landmarks and self.results.multi_handedness):
            return tips

        for handLms, handedness in zip(
            self.results.multi_hand_landmarks, self.results.multi_handedness
        ):
            label = handedness.classification[0].label  # "Left" or "Right"
            lm = handLms.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            tips[label] = (int(lm.x * w), int(lm.y * h))
        return tips


if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    exit(1)
