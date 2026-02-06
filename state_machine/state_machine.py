from core.data_types import PersonMemory
from state_machine import utils

class StateBase:
    def update(self, ctx):
        raise NotImplementedError
    

class Search(StateBase):
    GESTURE_HOLD_SECONDS = 1.0 # Time for the hand to be shown until stopping
    GESTURE_DECAY_SECONDS = 0.3 # Decay when hand is not showing
    COOLDOWN_SECONDS = 3.0 # Cooldown until looking for hands

    def __init__(self):
        self.gesture_start_time = None
        self.cooldown_start_time = None
        print("Searching...")

    def update(self, ctx, gesture="Open_Palm"):
        timestamp = ctx.perception["timestamp"]

        if ctx.cooldown:
            if self.cooldown_start_time is None:
                self.cooldown_start_time = timestamp

            elapsed = timestamp - self.cooldown_start_time
            if elapsed > self.COOLDOWN_SECONDS:
                ctx.cooldown = False

        if not ctx.cooldown:
            list_of_hands = ctx.perception["hands"]
            tracking_triggered, id_to_track = self.start_search_algorithm(
                list_of_hands, timestamp, ctx, gesture
            )
            if tracking_triggered:
                print("Target found!")
                ctx.target_found = True
                ctx.id_to_track = id_to_track
                ctx.cooldown = True  # Cooldown before looking for hands again

                return Track()

        return self

    

    def start_search_algorithm(self, hands, timestamp, ctx, gesture):
        
        matched_ids = set()

        if hands:
            for hand in hands:
                if hand.gesture_name == gesture:
                                        
                    person_id = hand.owner_id
                    matched_ids.add(person_id)

                    if person_id not in ctx.person_memory:
                        ctx.person_memory[person_id] = PersonMemory()

                    mem = ctx.person_memory[person_id]

                    if mem.gesture_start_time is None:
                        mem.gesture_start_time = timestamp

                    mem.gesture_elapsed_time = timestamp - mem.gesture_start_time

                    print(f"ID {person_id} held for {round(mem.gesture_elapsed_time,2)} seconds")

                    # If gesture held enough time, return track ID and clear memory
                    if mem.gesture_elapsed_time >= self.GESTURE_HOLD_SECONDS:
                        id_to_track = hand.owner_id
                        ctx.reset_person_memory()

                        return True, id_to_track
            
        
        utils.decay_all_memories(ctx=ctx,
                                 timestamp=timestamp,
                                 matched_ids=matched_ids,
                                 gesture_decay_seconds=self.GESTURE_DECAY_SECONDS
                                 )

        return False, None
    


class Track(StateBase):
    GESTURE_HOLD_SECONDS = 1.0 # Time for the hand to be shown until stopping
    GESTURE_DECAY_SECONDS = 0.3 # Decay when hand is not showing
    COOLDOWN_SECONDS = 3.0 # Cooldown until looking for hands
    GRACE_PERIOD_SECONDS = 1.0  # Grace period before transitioning to Stopped

    def __init__(self):
        self.gesture_start_time = None
        self.cooldown_start_time = None

    def update(self, ctx, gesture):
        timestamp = ctx.perception["timestamp"]

        id_to_track = ctx.id_to_track
        persons = ctx.perception["persons"]

        # iterate throught persons and return first match of where p.id == id_to_track
        target = next((p for p in persons if p.id == id_to_track), None)

        # If no target, start grace period timer
        if target is None:
            if ctx.target_lost_time is None:
                ctx.target_lost_time = timestamp  # Start grace period timer

            elapsed = timestamp - ctx.target_lost_time
            
            if elapsed >= self.GRACE_PERIOD_SECONDS:
                ctx.target_found = False
                ctx.target_lost = True
                ctx.target_lost_time = None  # Reset timer
                return Search()

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
            gesture_to_stop = self.search_for_gesture(ctx, timestamp, gesture)

            if gesture_to_stop:
                ctx.target_found = False
                ctx.target_lost = True
                ctx.cooldown = True

                return Search()

        return self

    def search_for_gesture(self, ctx, timestamp, gesture):
        matched_ids = set()
        list_of_hands = ctx.perception["hands"]
        if list_of_hands:
            for hand in list_of_hands:
                if (
                    hand.owner_id == ctx.id_to_track
                    and hand.gesture_name == gesture
                ):

                    person_id = hand.owner_id
                    matched_ids.add(person_id)

                    if person_id not in ctx.person_memory:
                        ctx.person_memory[person_id] = PersonMemory()

                    mem = ctx.person_memory[person_id]

                    if mem.gesture_start_time is None:
                        mem.gesture_start_time = timestamp

                    mem.gesture_elapsed_time = timestamp - mem.gesture_start_time

                    print(f"ID {person_id} held for {round(mem.gesture_elapsed_time,2)} seconds")
                    if mem.gesture_elapsed_time >= self.GESTURE_HOLD_SECONDS:
                        ctx.reset_person_memory()
                        return True
                    
        utils.decay_all_memories(ctx=ctx,
                                 timestamp=timestamp,
                                 matched_ids=matched_ids,
                                 gesture_decay_seconds=self.GESTURE_DECAY_SECONDS
                                 )  

        return False


class Stopped(StateBase):
    def update(self, ctx):
        import time
        
        print("Stopped! Searching in 3 seconds..")

        time.sleep(3)

        return Search()