from core.video_stream import VideoStream
from core.pipeline import Pipeline
from detection.person_detector import PersonDetector
from detection.hand_detector import HandDetector
from config.loader import load_detector_config
from state_machine.context import Context
from state_machine.state_machine import Search
from visualization.video_saver import VideoSaver
import visualization.write_on_frame
import cv2



def main():
    detector_cfg = load_detector_config("config/detector_config.yaml")
    what_to_detect = "both"

    source = 0
    #source = "example_videos/example3.mp4"

    stream = VideoStream(source=source)
    saver = VideoSaver(resolution=stream.get_resolution())
    context = Context()
    pipeline = Pipeline(
        person_detector=(
            PersonDetector(**detector_cfg["person_detector"])
            if not what_to_detect == "hands"
            else None
        ),
        hand_detector=(
            HandDetector(**detector_cfg["hand_detector"])
            if not what_to_detect == "persons"
            else None
        ),
    )


    try:
        state = Search()
        while True:
            frame, timestamp = stream.get_frame()
            if frame is None:
                break
            
            # Ensure states never observe stale perception.
            context.perception = None

            # Inference on the frame, detecting persons and hands
            results = pipeline.process_frame(frame, timestamp)
            
            context.perception = {
                **results,
                "timestamp": timestamp,
            }

            state = state.update(context)

            visualization.write_on_frame.visualize_all(frame, results, context)
            cv2.imshow('Video stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            saver.write_frame_to_video(frame)

    except KeyboardInterrupt:
        print("Interrupted by user")

    finally:
        stream.release()
        saver.release_video()
        cv2.destroyAllWindows()
        print("Released resources")


if __name__ == "__main__":
    main()
