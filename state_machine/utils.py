def decay_all_memories(ctx, timestamp, matched_ids, gesture_decay_seconds):
        for person_id, mem in ctx.person_memory.items():
            if person_id in matched_ids:
                continue

            if mem.gesture_start_time is None:
                continue

            elapsed = timestamp - mem.gesture_start_time
            elapsed_after_decay = elapsed - gesture_decay_seconds

            if elapsed_after_decay <= 0.0:
                mem.gesture_start_time = None
                mem.gesture_elapsed_time = 0.0
            else:
                mem.gesture_start_time = timestamp - elapsed_after_decay
                mem.gesture_elapsed_time = elapsed_after_decay