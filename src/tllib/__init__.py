"""Public package for tllib."""

from .specs.lock import load_lock


def specification_info() -> dict[str, str]:
    """Return validated metadata for the specification snapshot in use."""
    return load_lock().as_dict()


__all__ = ["domains", "specification_info"]
