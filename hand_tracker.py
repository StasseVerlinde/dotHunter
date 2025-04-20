import cv2
import mediapipe as mp

class HandTracker:
    """
    HandTracker uses MediaPipe to detect hand landmarks and provides
    methods to get the index-finger tip coordinates per hand, keyed
    by handedness.
    """
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, frame, draw=True):
        """
        Process the frame for hand landmarks. Optionally draw them.
        """
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks and draw:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(
                    frame,
                    handLms,
                    self.mpHands.HAND_CONNECTIONS
                )
        return frame

    def get_index_finger_tip(self, frame):
        """
        Solo mode helper: returns the first detected index-finger tip (x, y),
        or (None, None) if no hand.
        """
        h, w = frame.shape[:2]
        if self.results.multi_hand_landmarks:
            lm = self.results.multi_hand_landmarks[0]\
                      .landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            return int(lm.x * w), int(lm.y * h)
        return None, None

    def get_index_finger_tips_by_handedness(self, frame):
        """
        Returns a dict mapping "Left" and/or "Right" to the index-finger tip (x, y).
        Hands not seen simply aren’t in the dict.
        """
        tips = {}
        h, w = frame.shape[:2]
        if not (self.results.multi_hand_landmarks and
                self.results.multi_handedness):
            return tips

        for handLms, handedness in zip(self.results.multi_hand_landmarks,
                                        self.results.multi_handedness):
            label = handedness.classification[0].label  # "Left" or "Right"
            lm = handLms.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            tips[label] = (int(lm.x * w), int(lm.y * h))
        return tips

if __name__ == "__main__":
    print("This module is not meant to be run directly.")
    print("Please run demo.py to start the game.")