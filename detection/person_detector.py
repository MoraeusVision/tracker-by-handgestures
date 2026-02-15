from core.data_types import Person
import torch
from ultralytics import YOLO


class PersonDetector:
    def __init__(self, model_path, conf=0.7):
        self.model = YOLO(model_path)
        self.device = select_device()
        self.conf = conf

    def detect(self, frame):
        results = self.model.track(
            frame,
            conf=self.conf,
            device=self.device,
            classes=[0],
            persist=True,
            tracker="bytetrack.yaml",
            verbose=False,
            task="detect",
        )

        persons = []

        for r in results:
            if r.boxes is None:
                continue

            boxes = r.boxes.xyxy.cpu().numpy()
            scores = r.boxes.conf.cpu().numpy()
            ids = None

            if hasattr(r.boxes, "id") and r.boxes.id is not None:
                ids = r.boxes.id.cpu().numpy()

            for i, bbox in enumerate(boxes):
                person = Person(
                    id=int(ids[i]) if ids is not None else None,
                    bbox=bbox.astype(int),
                    confidence=float(scores[i]),
                )
                persons.append(person)

        return persons
    
# Device selection
def select_device():
    if torch.backends.mps.is_available() and torch.backends.mps.is_built():
        print("Using Apple Silicon GPU (MPS)")
        return "mps"  # Apple GPU
    elif torch.cuda.is_available():
        print("Using NVIDIA GPU (CUDA)")
        return "cuda"  # NVIDIA GPU
    else:
        print("Using CPU")
        return "cpu"  # fallback
