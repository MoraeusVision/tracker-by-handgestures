import cv2
import time

### Video stream only to create the frames to work with ###


class VideoStream:
    def __init__(self, source=0):
        """
        source:
            0            -> default webcam
            "video.mp4"  -> video file
        """
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open video source: {source}")
        else:
            print("Video initialized")

    def get_frame(self):
        """Get a single frame"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        timestamp = time.time()

        return frame, timestamp

    def get_resolution(self):
        """Get the resolution of the source"""
        frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (frame_width, frame_height)

        return frame_size

    def release(self):
        """Cleanup"""
        self.cap.release()
