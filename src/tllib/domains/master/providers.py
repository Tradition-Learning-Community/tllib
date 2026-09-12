"""Provider contracts for the master domain."""

from collections.abc import Iterable
from typing import Protocol

from .models import Master


class MasterProvider(Protocol):
    """Port used to retrieve master entities from an external source."""

    def list_masters(self) -> Iterable[Master]:
        """Return the available master entities."""
