"""
gramps.gen.utils.markdown.validate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generation-time validators for image paths and gramps: scheme URLs.

Called by md2gramplet.py during code generation; not used at runtime.
"""

import os
import sys

try:
    from gramps.gen.const import IMAGE_DIR as _IMAGE_DIR
except ImportError:
    _IMAGE_DIR = None

VALID_OBJ_TYPES = {
    "Person",
    "Family",
    "Event",
    "Place",
    "Source",
    "Citation",
    "Repository",
    "Media",
    "Note",
}

VALID_VIEW_CATEGORIES = {
    "people",
    "families",
    "events",
    "places",
    "sources",
    "citations",
    "repositories",
    "media",
    "notes",
    "geography",
    "charts",
    "dashboard",
}


def check_image(path, source_file=""):
    """Raise SystemExit if path cannot be resolved to an existing file."""
    loc = f" (from {source_file})" if source_file else ""

    if path.startswith("gramps:icon:"):
        if _IMAGE_DIR is None:
            return
        parts = path.split(":")
        name = parts[2]
        size = int(parts[3]) if len(parts) > 3 else 22
        for size_dir in [f"{size}x{size}", "scalable"]:
            for category in ("actions", "apps"):
                candidate = os.path.join(
                    _IMAGE_DIR, "hicolor", size_dir, category, f"{name}.png"
                )
                if os.path.exists(candidate):
                    return
        print(f"Error: icon not found{loc}: {name!r} (size {size})", file=sys.stderr)
        print(
            f"  Looked in: {os.path.join(_IMAGE_DIR, 'hicolor', f'{size}x{size}', '*')}",
            file=sys.stderr,
        )
        sys.exit(1)

    if path.startswith("gramps:image:"):
        filepath = path[len("gramps:image:") :]
    else:
        filepath = path

    if _IMAGE_DIR is None:
        return
    if os.path.isabs(filepath) and os.path.exists(filepath):
        return
    full = os.path.join(_IMAGE_DIR, filepath)
    if not os.path.exists(full):
        print(f"Error: image not found{loc}: {path!r}", file=sys.stderr)
        print(f"  Looked in: {full}", file=sys.stderr)
        sys.exit(1)


def check_gramps_url(url, source_file=""):
    """Validate a gramps: scheme URL at generation time."""
    loc = f" (from {source_file})" if source_file else ""
    parts = url.split(":")
    if len(parts) < 3:
        print(f"Error: malformed gramps: URL{loc}: {url!r}", file=sys.stderr)
        sys.exit(1)
    scheme = parts[1]
    if scheme == "view":
        category = parts[2]
        if category not in VALID_VIEW_CATEGORIES:
            print(f"Error: unknown view category{loc}: {category!r}", file=sys.stderr)
            print(
                f"  Valid: {', '.join(sorted(VALID_VIEW_CATEGORIES))}",
                file=sys.stderr,
            )
            sys.exit(1)
    elif scheme in ("edit", "nav"):
        if len(parts) < 4:
            print(
                f"Error: gramps:{scheme}: URL requires Type:GrampsID{loc}: {url!r}",
                file=sys.stderr,
            )
            sys.exit(1)
        obj_type = parts[2]
        if obj_type not in VALID_OBJ_TYPES:
            print(
                f"Error: unknown Gramps object type{loc}: {obj_type!r}",
                file=sys.stderr,
            )
            print(f"  Valid: {', '.join(sorted(VALID_OBJ_TYPES))}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Error: unknown gramps: scheme{loc}: {scheme!r}", file=sys.stderr)
        sys.exit(1)
