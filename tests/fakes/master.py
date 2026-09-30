"""Master-domain doubles reserved for tests."""

from tllib.domains.master.models import Master


class InMemoryMasterProvider:
    """Minimal in-memory implementation of the master provider port."""

    def list_masters(self) -> list[Master]:
        return [Master(name="Ada")]
