"""tarpeek: peek inside a tar archive without extracting it."""

from .core import ArchiveEmptyError, InvalidArchiveError, MemberInfo, iter_members

__all__ = ["ArchiveEmptyError", "InvalidArchiveError", "MemberInfo", "iter_members"]

__version__ = "0.1.0"
