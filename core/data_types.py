from dataclasses import dataclass
import numpy as np
from typing import Optional


@dataclass
class Person:
    id: Optional[int]
    bbox: np.ndarray
    confidence: Optional[float] = None


@dataclass
class Hand:
    gesture_name: Optional[str]
    confidence: Optional[float] = None
    landmarks: Optional[list] = None
    owner_id: Optional[int] = None