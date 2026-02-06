from state_machine.state_machine import Search
import cv2

########## PERSON VISUALIZATION ##########


def person_visualization(frame, results, ctx):
    bboxes = extract_bboxes(results)
    ids = extract_ids(results)

    for (x1, y1, x2, y2), pid in zip(bboxes, ids):
        x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

        # Decide appearance
        if ctx.target_found and pid == ctx.id_to_track:
            color = (0, 0, 255)
            label = f"ID: {pid} Tracked!"
        else:
            color = (0, 255, 0)
            label = f"ID: {pid}"

        # Draw bbox + text
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )

        # Draw gesture progress bar
        mem = ctx.person_memory.get(pid, None)
        if mem is not None and mem.gesture_start_time is not None:
            progress = mem.gesture_elapsed_time / Search.GESTURE_HOLD_SECONDS
            progress = max(0.0, min(1.0, progress))
            draw_progress_bar(frame, x1, y1, x2, y2, progress)


def extract_bboxes(results):
    bboxes = [p.bbox for p in results["persons"]]
    return bboxes


def extract_ids(results):
    ids = [p.id for p in results["persons"]]
    return ids


def draw_progress_bar(frame, x1, y1, x2, y2, progress):
    bar_height = y2 - y1
    bar_width = 8

    # Position to the right of the bbox
    bx1 = x2 + 6
    bx2 = bx1 + bar_width
    by1 = y1
    by2 = y2

    # Background (empty bar)
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (50, 50, 50), -1)

    # Filled part
    filled_height = int(bar_height * progress)
    fy1 = by2 - filled_height

    cv2.rectangle(frame, (bx1, fy1), (bx2, by2), (0, 255, 255), -1)

    # Border
    cv2.rectangle(frame, (bx1, by1), (bx2, by2), (255, 255, 255), 1)


########## HAND VISUALIZATION ##########


def hand_visualization(frame, results):
    pass


def extract_keypoints(frame, results):
    pass


########## VISUALIZE BOTH ##########


def visualize_all(frame, results, ctx):
    person_visualization(frame, results, ctx)
    hand_visualization(frame, results)
