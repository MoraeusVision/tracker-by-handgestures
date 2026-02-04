import cv2

class VideoSaver:
    def __init__(self, fps=30, resolution=(1280, 720)):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('saved_videos/output.mp4', fourcc, fps, resolution)

    def write_frame_to_video(self, frame):
        self.out.write(frame)

    def release_video(self):
        self.out.release()