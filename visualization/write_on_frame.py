import cv2

########## PERSON VISUALIZATION ##########

def person_visualization(frame, results):
    bboxes = extract_bboxes(results)
    ids = extract_ids(results)

    for (x1, y1, x2, y2), pid in zip(bboxes, ids):
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(
            frame,
            'ID: ' + str(pid),
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

def extract_bboxes(results):
    bboxes = [p.bbox for p in results['persons']]
    return bboxes

def extract_ids(results):
    ids = [p.id for p in results['persons']]
    return ids


########## HAND VISUALIZATION ##########

def hand_visualization(frame, results):
    pass


def extract_keypoints(frame, results):
    pass



########## VISUALIZE BOTH ##########

def visualize_all(frame, results):
    person_visualization(frame, results)
    hand_visualization(frame, results)



