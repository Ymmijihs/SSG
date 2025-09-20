import os
import shutil
from pathlib import Path
from typing import Iterable
from textnode import *

def clear_directory(dir_path: Path) -> None:
    """
    Delete *contents* of dir_path (files and subdirectories), leaving dir_path itself.
    Creates dir_path if it doesn't exist.
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    for entry in dir_path.iterdir():
        try:
            if entry.is_dir() and not entry.is_symlink():
                shutil.rmtree(entry)
                print(f"[DEL DIR]  {entry}")
            else:
                entry.unlink(missing_ok=True)
                print(f"[DEL FILE] {entry}")
        except Exception as e:
            raise RuntimeError(f"Failed to delete {entry}: {e}") from e


def copy_directory_recursive(src: Path, dst: Path) -> None:
    """
    Recursively copy all contents from src into dst.
    Assumes dst exists and is empty (use clear_directory first).
    """
    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")
    if not src.is_dir():
        raise NotADirectoryError(f"Source is not a directory: {src}")

    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        # Determine the relative path from src and the corresponding destination directory
        rel = root_path.relative_to(src)
        dst_root = dst / rel

        # Ensure destination subdirectory exists
        dst_root.mkdir(parents=True, exist_ok=True)

        # Copy files
        for name in files:
            s = root_path / name
            d = dst_root / name
            # If it's a symlink, try to copy the target content (follow links)
            try:
                if s.is_symlink():
                    # Resolve the link and copy the resolved file
                    target = s.resolve()
                    shutil.copy2(target, d)
                    print(f"[COPY LINK->FILE] {s} -> {d} (target: {target})")
                else:
                    shutil.copy2(s, d)
                    print(f"[COPY FILE] {s} -> {d}")
            except Exception as e:
                raise RuntimeError(f"Failed to copy file {s} -> {d}: {e}") from e

        # Create subdirectories explicitly (files handled above)
        for name in dirs:
            src_dir = root_path / name
            dst_dir = dst_root / name
            try:
                dst_dir.mkdir(parents=True, exist_ok=True)
                print(f"[ENSURE DIR] {dst_dir}")
            except Exception as e:
                raise RuntimeError(f"Failed to ensure directory {dst_dir}: {e}") from e


def copy_static_to_public(src: str = "static", dst: str = "public") -> None:
    """
    High-level helper:
    1) clears destination dir contents
    2) recursively copies everything from src into dst
    """
    src_path = Path(src).resolve()
    dst_path = Path(dst).resolve()

    if src_path == dst_path or str(dst_path).startswith(str(src_path) + os.sep):
        raise ValueError("Destination must not be the same as (or inside) the source directory.")

    print(f"[START] Copying from {src_path} -> {dst_path}")
    clear_directory(dst_path)
    copy_directory_recursive(src_path, dst_path)
    print(f"[DONE]  Copied to {dst_path}")


if __name__ == "__main__":
    # Example usage:
    copy_static_to_public("static", "public")
