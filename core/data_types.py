from dataclasses import dataclass
import numpy as np
from typing import Optional


@dataclass
class Person:
    id: Optional[int]
    bbox: np.ndarray
    confidence: Optional[float] = None
    gesture_start_time: Optional[float] = 0.0
    gesture_elapsed_time: Optional[float] = 0.0

    def update_gesture_elapsed_time(self, new_time: float):
        """Update the gesture elapsed time."""
        self.gesture_elapsed_time = new_time

    def update_gesture_start_time(self, new_time: float):
        """Update the gesture elapsed time."""
        self.gesture_start_time = new_time

    def reset_gesture_elapsed_time(self):
        """Reset the gesture elapsed time to zero."""
        self.gesture_elapsed_time = 0.0


@dataclass
class Hand:
    gesture_name: Optional[str]
    confidence: Optional[float] = None
    landmarks: Optional[list] = None
    owner_id: Optional[int] = None


@dataclass
class PersonMemory:
    gesture_start_time: float = None
    gesture_elapsed_time: float = 0.0
