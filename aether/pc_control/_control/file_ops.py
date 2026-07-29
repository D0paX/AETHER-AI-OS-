"""Private file-operation worker for PC control (M2.4).

PRIVATE to ``aether.pc_control`` — never imported outside this package, and
reached only through ``PCControlAPI``, which resolves every path and clears it
through ``SafetyValidator.validate_file_operation`` BEFORE calling anything here.
This layer performs the filesystem work on paths the caller has already resolved
and validated; it holds no policy of its own.

``search_files`` returns a LIST of candidates for the caller to choose from — it
never acts on any result. No action-taking function here derives its target from
a name, pattern, or query; ``move_file`` receives its exact, already-resolved
source and destination as arguments (the generalized M2.3 rule).
"""

from datetime import UTC, datetime
from pathlib import Path

import aiofiles
from pydantic import BaseModel, ConfigDict

from aether.core.logging import get_logger
from aether.pc_control.api import ActionResult

logger = get_logger(__name__)

# Cap on how many candidates a single search returns, so a search over a huge
# tree stays bounded (the caller picks from these; it is not an action).
_SEARCH_RESULT_LIMIT = 1000

# Glob metacharacters — if the query has none, it is treated as a substring of
# the file name rather than an exact match.
_GLOB_CHARS = set("*?[]")


class FileSearchFilter(BaseModel):
    """Optional filters narrowing a file search.

    Attributes:
        extensions: If set, keep only files whose extension is in this list
            (leading dot optional, case-insensitive).
        modified_after: If set, keep only files modified at or after this time.
    """

    extensions: list[str] | None = None
    modified_after: datetime | None = None


class FileInfo(BaseModel):
    """A file found by a search.

    Attributes:
        path: The absolute path.
        size_bytes: File size on disk.
        modified_at: Last-modified time (UTC).
    """

    model_config = ConfigDict(frozen=True)

    path: str
    size_bytes: int
    modified_at: datetime


class FileContent(BaseModel):
    """The (possibly truncated) content of a read file.

    Attributes:
        path: The absolute path read.
        content: The decoded text (UTF-8, undecodable bytes replaced).
        size_bytes: The file's full size on disk.
        truncated: True when the file exceeded the read limit and only a prefix
            is present in ``content``.
    """

    model_config = ConfigDict(frozen=True)

    path: str
    content: str
    size_bytes: int
    truncated: bool


def search_files(query: str, root: Path, filters: FileSearchFilter) -> list[FileInfo]:
    """Search under ``root`` for files matching ``query`` and ``filters``.

    Args:
        query: A glob pattern, or — if it contains no glob metacharacters — a
            substring matched against file names.
        root: The already-resolved, already-validated directory to search under.
        filters: Optional extension / modified-after filters.

    Returns:
        Up to ``_SEARCH_RESULT_LIMIT`` matching files as FileInfo candidates.
        This is a list to choose from; it is never itself acted upon.
    """
    pattern = query if any(c in query for c in _GLOB_CHARS) else f"*{query}*"
    wanted_exts = (
        {e.lower().lstrip(".") for e in filters.extensions} if filters.extensions else None
    )

    results: list[FileInfo] = []
    for candidate in root.rglob(pattern):
        if len(results) >= _SEARCH_RESULT_LIMIT:
            break
        if not candidate.is_file():
            continue
        ext = candidate.suffix.lower().lstrip(".")
        if wanted_exts is not None and ext not in wanted_exts:
            continue
        try:
            stat = candidate.stat()
        except OSError:
            continue
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
        if filters.modified_after is not None and modified_at < filters.modified_after:
            continue
        results.append(
            FileInfo(
                path=str(candidate),
                size_bytes=stat.st_size,
                modified_at=modified_at,
            )
        )
    logger.info("pc_control.search_files", root=str(root), matches=len(results))
    return results


async def read_file(path: Path, cap_bytes: int) -> FileContent:
    """Read a file, truncating to ``cap_bytes`` if it is larger.

    Args:
        path: The already-resolved, already-validated file path.
        cap_bytes: Maximum number of bytes to read into the returned content.

    Returns:
        A FileContent; ``truncated`` is True when the file on disk is larger than
        ``cap_bytes`` (only the first ``cap_bytes`` are returned).

    Raises:
        OSError: If the file cannot be stat-ed or opened (e.g. it does not exist).
    """
    size = path.stat().st_size
    truncated = size > cap_bytes
    to_read = cap_bytes if truncated else size
    async with aiofiles.open(path, "rb") as handle:
        data = await handle.read(to_read)
    content = data.decode("utf-8", errors="replace")
    logger.info(
        "pc_control.read_file",
        path=str(path),
        size_bytes=size,
        truncated=truncated,
    )
    return FileContent(path=str(path), content=content, size_bytes=size, truncated=truncated)


def move_file(source: Path, destination: Path) -> ActionResult:
    """Move ``source`` to ``destination`` (both already resolved and validated).

    Uses ``Path.replace``, which renames within a filesystem and overwrites an
    existing destination atomically — no separate delete step, and no name-based
    lookup: it acts on exactly these two paths. Overwriting an existing
    destination has already been gated by ``confirmation_token`` upstream.

    Args:
        source: The exact file to move.
        destination: The exact target path.

    Returns:
        An ActionResult describing the outcome.
    """
    try:
        source.replace(destination)
    except OSError as exc:
        logger.info(
            "pc_control.move_file",
            source=str(source),
            destination=str(destination),
            success=False,
            message=str(exc),
        )
        return ActionResult(
            success=False,
            message=f"Move failed: {exc}",
            process_id=None,
        )
    logger.info(
        "pc_control.move_file",
        source=str(source),
        destination=str(destination),
        success=True,
    )
    return ActionResult(
        success=True,
        message=f"Moved '{source}' -> '{destination}'.",
        process_id=None,
    )
