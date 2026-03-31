"""
gramps.gen.utils.markdown.parse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Pure-Python tokenizer for the md2gramplet markdown dialect.

No GTK, no Gramps GUI dependencies.
"""

import re

# ── Regexes ────────────────────────────────────────────────────────────────────

_LINK_RE = re.compile(r"^-\s+(~?)\[([^\]]*)\]\(([^)]*)\)\s*$")
_HEAD_RE = re.compile(r"^(#{1,6})\s+(.*)")
# Block image: ![alt](src) alone on a line
_BLOCK_IMG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$")
# Icon at the start of content: ![alt](src) text...
_ICON_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s+(.+)")


def _strip_quotes(s):
    """Remove surrounding single or double quotes."""
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def parse_front_matter(text):
    """
    Parse YAML-like front matter delimited by --- lines.
    Returns (config: dict, body: str).

    Supports:
        key: scalar value
        key:
          - list item
        key:
          subkey: value
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    yaml_src = text[4:end]
    body = text[end + 5 :]

    config = {}
    lines = yaml_src.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\w+):\s*(.*)", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val:
            config[key] = _strip_quotes(val)
            i += 1
        else:
            items = []
            kv = {}
            i += 1
            while i < len(lines) and lines[i] and lines[i][0] in " \t":
                sub = lines[i].strip()
                if sub.startswith("- "):
                    items.append(sub[2:].strip())
                elif ":" in sub:
                    k, _, v = sub.partition(":")
                    kv[k.strip()] = _strip_quotes(v.strip())
                i += 1
            config[key] = kv if kv else items
    return config, body


def parse_img_src(src):
    """Parse image src into (path, width, align).

    Handles:
        gramps:icon:name:size      -> (src, None, "left")  — size embedded in URI
        gramps:image:file|w|a     -> ("gramps:image:file", w, a)
        plain/path|w|a             -> ("plain/path", w, a)
    """
    if src.startswith("gramps:icon:"):
        return src, None, "left"
    parts = src.split("|")
    path = parts[0]
    width = int(parts[1]) if len(parts) > 1 and parts[1] else None
    align = parts[2] if len(parts) > 2 and parts[2] else "left"
    return path, width, align


def parse_markdown(text):
    """
    Parse a markdown body into a list of block tokens.

    Token shapes:
        {'type': 'heading',     'level': int, 'text': str, 'icon': str|None}
        {'type': 'paragraph',   'text': str}
        {'type': 'block_image', 'path': str, 'width': int|None, 'align': str}
        {'type': 'icon_para',   'icon': str, 'text': str}
        {'type': 'link',        'text': str, 'url': str, 'translate': bool}
    """
    blocks = []
    para_lines = []

    def flush_para():
        if para_lines:
            blocks.append({"type": "paragraph", "text": " ".join(para_lines)})
            para_lines.clear()

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            flush_para()
            continue

        m_head = _HEAD_RE.match(stripped)
        if m_head:
            flush_para()
            level = len(m_head.group(1))
            head_text = m_head.group(2).strip()
            icon = None
            m_icon = _ICON_RE.match(head_text)
            if m_icon:
                icon = m_icon.group(2).strip()  # src from (...)
                head_text = m_icon.group(3).strip()  # text after )
            blocks.append(
                {"type": "heading", "level": level, "text": head_text, "icon": icon}
            )
            continue

        m_link = _LINK_RE.match(stripped)
        if m_link:
            flush_para()
            blocks.append(
                {
                    "type": "link",
                    "text": m_link.group(2),
                    "url": m_link.group(3),
                    "translate": m_link.group(1) != "~",
                }
            )
            continue

        m_bimg = _BLOCK_IMG_RE.match(stripped)
        if m_bimg:
            flush_para()
            path, width, align = parse_img_src(m_bimg.group(2).strip())
            blocks.append(
                {
                    "type": "block_image",
                    "path": path,
                    "width": width,
                    "align": align,
                }
            )
            continue

        m_icon = _ICON_RE.match(stripped)
        if m_icon:
            flush_para()
            blocks.append(
                {
                    "type": "icon_para",
                    "icon": m_icon.group(2).strip(),  # src from (...)
                    "text": m_icon.group(3).strip(),  # text after )
                }
            )
            continue

        para_lines.append(stripped)

    flush_para()
    return blocks
