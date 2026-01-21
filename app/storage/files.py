from __future__ import annotations

import os
from pathlib import Path
from app.core.config import settings

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def storage_root() -> Path:
    return Path(settings.STORAGE_DIR)

def write_bytes(relative_path: str, data: bytes) -> Path:
    root = storage_root()
    dest = root / relative_path
    ensure_dir(dest.parent)
    dest.write_bytes(data)
    return dest

def write_text(relative_path: str, text: str, encoding: str = "utf-8") -> Path:
    root = storage_root()
    dest = root / relative_path
    ensure_dir(dest.parent)
    dest.write_text(text, encoding=encoding)
    return dest
