"""Filesystem archive adapter.

Implements ArchiveCreator port by copying files between local directories.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from pes.ports.archive_port import ArchiveCreator


class FilesystemArchiveCreator(ArchiveCreator):
    """Creates archives by copying files on the local filesystem."""

    def create_archive(self, source_dir: str, dest_dir: str) -> None:
        """Copy all regular files from source_dir into dest_dir."""
        source = Path(source_dir)
        target = Path(dest_dir)
        for item in source.iterdir():
            if item.is_file():
                shutil.copy2(str(item), str(target / item.name))
