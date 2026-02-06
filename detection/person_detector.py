from core.data_types import Person

from ultralytics import YOLO


class PersonDetector:
    def __init__(self, model_path, device="cpu", conf=0.7):
        self.model = YOLO(model_path)
        self.device = device
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
