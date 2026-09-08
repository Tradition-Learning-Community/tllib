"""Registry for master-domain providers."""

from .errors import MasterError
from .providers import MasterProvider


class MasterRegistry:
    """Register and retrieve the provider used by the master domain."""

    def __init__(self) -> None:
        self._provider: MasterProvider | None = None

    def register(self, provider: MasterProvider) -> None:
        """Set the active provider."""
        self._provider = provider

    def provider(self) -> MasterProvider:
        """Return the active provider or fail with a domain-specific error."""
        if self._provider is None:
            raise MasterError("No master provider has been registered")
        return self._provider