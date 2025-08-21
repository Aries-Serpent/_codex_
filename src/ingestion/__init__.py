"""Basic file ingestion utilities.

This module defines the :class:`Ingestor` class which provides a small helper
for reading textual data from files.  The implementation is intentionally
minimal and serves as a starting point for future ingestion features.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union


class Ingestor:
    """Simple ingestor that reads text from files."""

    def ingest(self, path: Union[str, Path]) -> str:
        """Read and return text content from a file.

        Parameters
        ----------
        path:
            Filesystem path to a text file.

        Returns
        -------
        str
            The textual contents of the file.

        Raises
        ------
        FileNotFoundError
            If ``path`` does not exist or is not a regular file.
        OSError
            If the file exists but cannot be read.
        """

        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(f"No such file: {file_path}")
        return file_path.read_text()
