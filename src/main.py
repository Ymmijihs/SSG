import os
import shutil
from pathlib import Path
from textnode import *


def clear_directory(dir_path: Path) -> None:
    """
    Delete *contents* of dir_path (files and subdirectories), leaving dir_path itself.
    Creates dir_path if it doesn't exist.
    """
    dir_path.mkdir(parents=True, exist_ok=True)
    for entry in dir_path.iterdir():
        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
            print(f"[DEL DIR]  {entry}")
        else:
            entry.unlink(missing_ok=True)
            print(f"[DEL FILE] {entry}")


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
        rel = root_path.relative_to(src)
        dst_root = dst / rel

        dst_root.mkdir(parents=True, exist_ok=True)

        for name in files:
            s = root_path / name
            d = dst_root / name
            if s.is_symlink():
                target = s.resolve()
                shutil.copy2(target, d)
                print(f"[COPY LINK->FILE] {s} -> {d} (target: {target})")
            else:
                shutil.copy2(s, d)
                print(f"[COPY FILE] {s} -> {d}")

        for name in dirs:
            dst_dir = dst_root / name
            dst_dir.mkdir(parents=True, exist_ok=True)
            print(f"[ENSURE DIR] {dst_dir}")


def copy_static_to_public(src: str = "static", dst: str = "public") -> None:
    """
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


def generate_page(from_path: str | Path, template_path: str | Path, dest_path: str | Path) -> None:
    """
    Build a single HTML page from a markdown source and an HTML template.
    Replaces {{ Title }} and {{ Content }} in the template, and writes to dest_path.
    """
    src = Path(from_path)
    tpl = Path(template_path)
    dest = Path(dest_path)

    print(f"[PAGE] Generating page from {src} to {dest} using {tpl}")

    markdown = src.read_text(encoding="utf-8")
    template = tpl.read_text(encoding="utf-8")

    root_node = markdown_to_html_node(markdown)
    content_html = root_node.to_html()

    title = extract_title(markdown)

    final_html = (
        template
        .replace("{{ Title }}", title)
        .replace("{{ Content }}", content_html)
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(final_html, encoding="utf-8")
    print(f"[PAGE] Wrote {dest}")



def generate_pages_recursive(
    dir_path_content: str | Path,
    template_path: str | Path,
    dest_dir_path: str | Path,
) -> None:
    """
    Crawl dir_path_content for all *.md files and generate corresponding .html
    files under dest_dir_path, preserving the directory structure.

    Example:
      content/blog/post.md  -> public/blog/post.html
      content/index.md      -> public/index.html
    """
    content_root = Path(dir_path_content)
    dest_root = Path(dest_dir_path)
    tpl_path = Path(template_path)

    if not content_root.exists():
        raise FileNotFoundError(f"Content directory not found: {content_root}")
    if not tpl_path.exists():
        raise FileNotFoundError(f"Template not found: {tpl_path}")

    # Load template once
    template = tpl_path.read_text(encoding="utf-8")

    for md_path in content_root.rglob("*.md"):
        # Compute output path
        rel = md_path.relative_to(content_root)              # e.g., blog/post.md
        out_rel = rel.with_suffix(".html")                   # e.g., blog/post.html
        dest_path = dest_root / out_rel

        print(f"[PAGE] Generating page from {md_path} to {dest_path} using {tpl_path}")

        # Read markdown
        markdown = md_path.read_text(encoding="utf-8")

        # Convert markdown to HTML
        root_node = markdown_to_html_node(markdown)
        content_html = root_node.to_html()

        # Extract title (will raise if missing H1)
        title = extract_title(markdown)

        # Inject into template
        final_html = (
            template
            .replace("{{ Title }}", title)
            .replace("{{ Content }}", content_html)
        )

        # Ensure destination directory exists and write file
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(final_html, encoding="utf-8")
        print(f"[PAGE] Wrote {dest_path}")


        
if __name__ == "__main__":
    public_dir = Path("public")

    # Copy static -> public (this also clears public first)
    copy_static_to_public("static", "public")

    # Generate ALL markdown pages recursively
    generate_pages_recursive(
        dir_path_content="content",
        template_path="template.html",
        dest_dir_path="public",
    )
