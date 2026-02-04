class StateBase:
    def update(self, ctx):
        raise NotImplementedError
    

class Search(StateBase):
    GESTURE_HOLD_SECONDS = 1.0
    GESTURE_DECAY_SECONDS = 0.5

    def __init__(self):
        self.gesture_start_time = None
        print("Searching...")

    def update(self, ctx):
        frame_id = ctx.perception["frame_id"]
        timestamp = ctx.perception["timestamp"]

        if frame_id % 3 == 0:
            list_of_hands = ctx.perception["hands"]
            tracking_triggered, id_to_track = self.start_search_algorithm(
                list_of_hands, timestamp
            )
            if tracking_triggered:
                print("Target found!")
                ctx.target_found = True
                ctx.id_to_track = id_to_track
                ctx.cooldown = True  # Cooldown before looking for hands again

                return Track()

        return self

    def _decay_gesture_timer(self, timestamp):
        if self.gesture_start_time is None:
            return

        elapsed = timestamp - self.gesture_start_time
        elapsed_after_decay = elapsed - self.GESTURE_DECAY_SECONDS
        if elapsed_after_decay <= 0.0:
            self.gesture_start_time = None
            return

        self.gesture_start_time = timestamp - elapsed_after_decay

    def start_search_algorithm(self, hands, timestamp):
        if hands:
            matched_this_frame = False
            for hand in hands:
                if hand.gesture_name == "Open_Palm":
                    matched_this_frame = True
                    if self.gesture_start_time is None:
                        self.gesture_start_time = timestamp
                        print("Open palm detected, starting timer")

                    elapsed = timestamp - self.gesture_start_time

                    print(f"Open palm held for {elapsed} seconds")
                    if elapsed >= self.GESTURE_HOLD_SECONDS:
                        id_to_track = hand.owner_id

                        return True, id_to_track
            if not matched_this_frame:
                self._decay_gesture_timer(timestamp)
        else:
            self._decay_gesture_timer(timestamp)

        return False, None
    


class Track(StateBase):
    GESTURE_HOLD_SECONDS = 1.0 # Time for the hand to be shown until stopping
    GESTURE_DECAY_SECONDS = 0.5 # Decay when hand is not showing
    COOLDOWN_SECONDS = 3.0 # Cooldown until looking for hands
    GRACE_PERIOD_SECONDS = 1.0  # Grace period before transitioning to Stopped

    def __init__(self):
        self.gesture_start_time = None
        self.cooldown_start_time = None

    def update(self, ctx):
        frame_id = ctx.perception["frame_id"]
        timestamp = ctx.perception["timestamp"]

        id_to_track = ctx.id_to_track
        persons = ctx.perception["persons"]

        # iterate throught persons and return first match of where p.id == id_to_track
        target = next((p for p in persons if p.id == id_to_track), None)

        # If no target, start grace period timer
        if target is None:
            print("Target lost this frame")
            
            if ctx.target_lost_time is None:
                ctx.target_lost_time = timestamp  # Start grace period timer

            elapsed = timestamp - ctx.target_lost_time
            print(f"Target lost time is {elapsed} seconds")
            if elapsed >= self.GRACE_PERIOD_SECONDS:
                ctx.target_found = False
                ctx.target_lost = True
                ctx.target_lost_time = None  # Reset timer
                return Stopped()

            return self  # Stay in Track state during grace period

        # Reset grace period timer if target is found again
        ctx.target_lost_time = None

        # Cooldown before looking for hands again
        if ctx.cooldown:
            if self.cooldown_start_time is None:
                self.cooldown_start_time = timestamp

            elapsed = timestamp - self.cooldown_start_time
            if elapsed > self.COOLDOWN_SECONDS:
                ctx.cooldown = False

        gesture_to_stop = False
        if not ctx.cooldown:
            if frame_id % 3 == 0:
                gesture_to_stop = self.search_for_gesture(ctx, timestamp)

            if gesture_to_stop:
                ctx.target_found = False
                ctx.target_lost = True

                return Stopped()

        return self

    def _decay_gesture_timer(self, timestamp):
        if self.gesture_start_time is None:
            return

        elapsed = timestamp - self.gesture_start_time
        elapsed_after_decay = elapsed - self.GESTURE_DECAY_SECONDS
        if elapsed_after_decay <= 0.0:
            self.gesture_start_time = None
            return

        # Shift start time forward so remaining elapsed is reduced (decay)
        self.gesture_start_time = timestamp - elapsed_after_decay

    def search_for_gesture(self, ctx, timestamp):
        list_of_hands = ctx.perception["hands"]
        if list_of_hands:
            matched_this_frame = False
            for hand in list_of_hands:
                if (
                    hand.owner_id == ctx.id_to_track
                    and hand.gesture_name == "Open_Palm"
                ):
                    matched_this_frame = True
                    if self.gesture_start_time is None:
                        self.gesture_start_time = timestamp
                        print("Open palm detected while tracking, starting timer")

                    elapsed = timestamp - self.gesture_start_time
                    print(f"Open palm held for {elapsed} seconds")
                    if elapsed >= self.GESTURE_HOLD_SECONDS:
                        return True
            if not matched_this_frame:
                self._decay_gesture_timer(timestamp)
        else:
            self._decay_gesture_timer(timestamp)

        return False


class Stopped(StateBase):
    def update(self, ctx):
        import time
        
        print("Stopped! Searching in 3 seconds..")

        time.sleep(3)

        return Search()