"""Master domain contracts and implementations."""

from .errors import MasterError
from .models import Master
from .registry import MasterRegistry

__all__ = ["Master", "MasterError", "MasterRegistry"]
