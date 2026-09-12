"""Operations for the master domain."""

from collections.abc import Iterable

from .models import Master
from .providers import MasterProvider


def list_masters(provider: MasterProvider) -> Iterable[Master]:
    """Return masters supplied by the configured port."""
    return provider.list_masters()
