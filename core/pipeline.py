### The pipeline for the project ###


class Pipeline:
    def __init__(self, person_detector, hand_detector):
        self.person_detector = person_detector
        self.hand_detector = hand_detector

    def process_frame(self, frame, timestamp, frame_id):
        """Object detection in the frame"""

        # Detect people in the frame
        persons_detected = (
            self.person_detector.detect(frame) if self.person_detector else None
        )

        hands_detected = None
        if frame_id % 3 == 0:  # To increase fps on the tracking
            # Detect hands in the frame
            hands_detected = (
                self.hand_detector.detect(frame, persons_detected)
                if self.hand_detector
                else None
            )
        return {
            "persons": persons_detected,  # ID, bbox and confidence
            "hands": hands_detected,  # Gesture, confidence, landmarks and owner ID
        }