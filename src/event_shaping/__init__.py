"""Event shaping: debounce and throttle."""

from .debounce import DebounceGate
from .interfaces import EventGate
from .throttle import ThrottleGate

__all__ = ["EventGate", "DebounceGate", "ThrottleGate"]
