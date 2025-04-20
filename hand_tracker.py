import cv2
import mediapipe as mp

class HandTracker:
    """
    HandTracker uses MediaPipe to detect hand landmarks and provides the index finger tip coordinates.
    """
    def __init__(self, mode=False, maxHands=1, detectionCon=0.7, trackCon=0.7):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Initialize MediaPipe Hands.
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        # For drawing hand landmarks (optional)
        self.mpDraw = mp.solutions.drawing_utils

    def find_hands(self, frame, draw=True):
        """
        Processes the frame to detect hands and optionally draws landmarks.
        Returns the frame with landmarks drawn (if draw=True).
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
        Returns (x, y) pixel coordinates of the index finger tip if detected;
        otherwise returns (None, None).
        """
        frame_height, frame_width = frame.shape[:2]
        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[self.mpHands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_tip.x * frame_width)
            y = int(index_tip.y * frame_height)
            return x, y
        return None, None

