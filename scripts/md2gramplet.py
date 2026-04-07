#!/usr/bin/env python3
"""
md2gramplet.py — Markdown to Gramplet code generator.

Converts a Markdown file with YAML front matter into a Gramps gramplet Python
file that uses Gtk.TextBuffer directly, supporting images and inline styling.

Usage:
    python scripts/md2gramplet.py input.md output.py

YAML Front Matter Fields (between --- delimiters):
    class        Required. Python class name.
    copyright    List of "YEAR  Author Name <email>" strings.
    description  Docstring for the generated class.
    imports      List of extra import lines beyond the fixed set.
    vars         Dict of name: "python_expression" — emitted as local
                 variables at the top of display_text(), available as
                 URL targets.

Markdown Constructs:
    ## Heading Text            Bold heading (translated).
    ## ![](src) Heading        Icon beside heading.
    paragraph text             Plain translated paragraph.
    **bold** and *italic*      Inline formatting within paragraphs.
    ![](src) text              Small icon floated left, text beside it.
    ![](src)                   Block image on its own line.
    - [Text](url)              Translated bullet link.
    - ~[Text](url)             Untranslated bullet link (filenames, etc.).

URL Syntax in Links:
    https://example.com          Literal URL string.
    {VARNAME}                    Python variable/constant reference.
    {VARNAME}suffix              Concatenation: VARNAME + "suffix".
    wiki:PageName                wiki("PageName")
    wiki_manual:PageName         wiki("PageName", manual=True)
    wiki:{VARNAME}               wiki(VARNAME)  — variable holds page name

Image src URI schemes:
    gramps:icon:name:size      GTK theme icon (name without .png, size in px).
    gramps:image:file|w|a      File relative to IMAGE_DIR; optional |width|align.
    plain/path|w|a             Legacy plain path relative to IMAGE_DIR.

Gramps Object Links:
    gramps:edit:Person:I0001   Opens editor for that Gramps object.
    gramps:nav:Person:I0001    Navigates view to that object.
    gramps:view:geography      Switches to a view category.
"""

import os
import re
import sys
from pathlib import Path

# Ensure the repository root is on the path so gramps.gen.utils.markdown is importable.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from gramps.gen.utils.markdown import (
    check_gramps_url,
    check_image,
    parse_front_matter,
    parse_markdown,
)

# ── License template ──────────────────────────────────────────────────────────

_LICENSE = """\
# Gramps - a GTK+/GNOME based genealogy program
#
{copyright}#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
"""

# ── Fixed imports ─────────────────────────────────────────────────────────────

_FIXED_IMPORTS_TOP = """
# ------------------------------------------------------------------------
#
# Gtk modules
#
# ------------------------------------------------------------------------
from gi.repository import Gtk, Pango, GdkPixbuf

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
"""

_FIXED_IMPORTS_BOTTOM = """\
from gramps.gen.plug import Gramplet
from gramps.gui.display import display_url
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
"""

# ── Helper imports template ───────────────────────────────────────────────────

_HELPERS = """\
# ------------------------------------------------------------------------
#
# Runtime helpers  (edit the .md source, not this generated file)
#
# ------------------------------------------------------------------------
from gramps.gui.widgets.markdown_render import _ins_image, _ins_link, _render_inline, wiki
"""

# ── Gramps link handler method template ──────────────────────────────────────

_GRAMPS_LINK_METHOD = """\
    def _handle_gramps_link(self, url):
        \"\"\"Dispatch a gramps: scheme URL to the appropriate Gramps action.\"\"\"
        from gramps.gui.widgets.markdown_render import _handle_gramps_link as _dispatch

        _dispatch(url, self.dbstate, self.uistate)

"""


# ── URL -> Python expression ──────────────────────────────────────────────────


def _url_to_expr(url):
    """Convert a markdown URL spec to a Python expression string."""
    if url.startswith("wiki_manual:"):
        page = url[len("wiki_manual:") :]
        return f"wiki({_page_arg(page)}, manual=True)"

    if url.startswith("wiki:"):
        page = url[len("wiki:") :]
        return f"wiki({_page_arg(page)})"

    if "{" in url:
        parts = re.split(r"\{(\w+)\}", url)
        exprs = []
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                if part:
                    exprs.append(f'"{part}"')
            else:
                exprs.append(part)
        return " + ".join(exprs) if exprs else '""'

    return f'"{url}"'


def _page_arg(page):
    """Return a Python argument for a wiki page (quoted string or bare variable)."""
    if page.startswith("{") and page.endswith("}"):
        return page[1:-1]
    return f'"{page}"'


# ── Python string quoting ─────────────────────────────────────────────────────


def _best_quote(text):
    """Wrap text in the most appropriate Python quote character."""
    has_dq = '"' in text
    has_sq = "'" in text
    if has_dq and not has_sq:
        return f"'{text}'"
    if has_dq and has_sq:
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return f'"{text}"'


def _py_str(text):
    """Return a single Python string literal for text (no newline suffix)."""
    return _best_quote(text)


def _py_translated(text, with_nn=False):
    """
    Return a _("...") or multi-line _(\\n    "..."\\n    "..."\\n) expression.

    with_nn: if True, appends \\n\\n inside the _() call.
    """
    suffix = r"\n\n" if with_nn else ""
    # Budget: "        _render_inline(buf, " = 28 chars, "))" = 2 -> 49 left
    oneliner_budget = 49
    single = _best_quote(text + suffix)
    if len(single) + 4 <= oneliner_budget:
        return f"_({single})"

    words = text.split(" ")
    segs = []
    cur = ""
    for word in words:
        candidate = (cur + " " + word) if cur else word
        if len(candidate) > 68 and cur:
            segs.append(cur)
            cur = word
        else:
            cur = candidate
    if cur:
        segs.append(cur)

    lines = []
    for idx, seg in enumerate(segs):
        content = seg if idx == 0 else " " + seg
        if idx == len(segs) - 1:
            content += suffix
        lines.append("            " + _best_quote(content))

    return "_(\n" + "\n".join(lines) + "\n        )"


# ── display_text() body generator ────────────────────────────────────────────


def _display_body(blocks, vars_dict):
    """Generate the indented body of display_text()."""
    out = []
    sp = "        "  # 8-space indent inside a method

    if vars_dict:
        for name, expr in vars_dict.items():
            out.append(f"{sp}{name} = {expr}")
        out.append("")

    out.append(f"{sp}buf = self.buffer")
    out.append(f'{sp}buf.set_text("")')
    out.append(f"{sp}links = []")

    for block in blocks:
        btype = block["type"]
        out.append("")  # blank line between blocks for readability

        if btype == "heading":
            level = block.get("level", 2)
            tag = f"h{level}"
            txt = block["text"]
            icon = block.get("icon")
            if icon:
                out.append(f"{sp}_ins_image(buf, {_py_str(icon)})")
                out.append(f'{sp}buf.insert(buf.get_end_iter(), " ")')
            out.append(f"{sp}start = buf.get_char_count()")
            out.append(f"{sp}buf.insert(buf.get_end_iter(), _({_py_str(txt)}))")
            out.append(
                f"{sp}buf.apply_tag_by_name("
                f'"{tag}", buf.get_iter_at_offset(start), buf.get_end_iter())'
            )
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "\\n\\n")')

        elif btype == "paragraph":
            txt = block["text"]
            expr = _py_translated(txt, with_nn=False)
            out.append(f"{sp}_render_inline(buf, {expr})")
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "\\n\\n")')

        elif btype == "block_image":
            path = block["path"]
            width = block["width"]
            align = block["align"]
            args = _py_str(path)
            if width:
                args += f", width={width}"
            if align != "left":
                args += f', align="{align}"'
            out.append(f"{sp}_ins_image(buf, {args})")
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "\\n\\n")')

        elif btype == "icon_para":
            icon = block["icon"]
            txt = block["text"]
            expr = _py_translated(txt, with_nn=False)
            out.append(f"{sp}_ins_image(buf, {_py_str(icon)})")
            out.append(f'{sp}buf.insert(buf.get_end_iter(), " ")')
            out.append(f"{sp}_render_inline(buf, {expr})")
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "\\n\\n")')

        elif btype == "link":
            txt = block["text"]
            url_expr = _url_to_expr(block["url"])
            text_expr = f"_({_py_str(txt)})" if block["translate"] else _py_str(txt)
            is_gramps = block["url"].startswith("gramps:")
            tag_arg = ', "gramps_link"' if is_gramps else ""
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "  \\u2022 ")')
            out.append(f"{sp}_ins_link(buf, links, {text_expr}, {url_expr}{tag_arg})")
            out.append(f'{sp}buf.insert(buf.get_end_iter(), "\\n\\n")')

    out.append("")
    out.append(f"{sp}self._links = links")
    return "\n".join(out)


# ── Full file generator ───────────────────────────────────────────────────────


def generate(config, blocks):
    """Assemble and return the complete Python gramplet source."""
    classname = config.get("class", "MyGramplet")
    description = config.get("description", f"Displays {classname} content.")
    copyright_items = config.get("copyright", [])
    extra_imports = config.get("imports", [])
    vars_dict = config.get("vars", {})

    has_gramps_links = any(
        b["type"] == "link" and b["url"].startswith("gramps:") for b in blocks
    )

    if has_gramps_links:
        link_action = (
            'if url.startswith("gramps:"):\n'
            "                    self._handle_gramps_link(url)\n"
            "                else:\n"
            "                    display_url(url)"
        )
        gramps_link_method = _GRAMPS_LINK_METHOD
    else:
        link_action = "display_url(url)"
        gramps_link_method = ""

    body = _display_body(blocks, vars_dict)

    parts = []

    # 1. License header
    cr_lines = "".join(f"# Copyright (C) {c}\n" for c in copyright_items)
    parts.append(_LICENSE.format(copyright=cr_lines))

    # 2. Fixed imports with extra imports merged into the Gramps section
    parts.append(_FIXED_IMPORTS_TOP)
    if extra_imports:
        parts.append("\n".join(extra_imports) + "\n")
    parts.append(_FIXED_IMPORTS_BOTTOM)

    # 3. Helper imports (delegates to markdown_render)
    parts.append(_HELPERS)

    # 4. Class
    parts.append(f"""
# ------------------------------------------------------------------------
#
# {classname}
#
# ------------------------------------------------------------------------


class {classname}(Gramplet):
    \"\"\"{description}\"\"\"

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        \"\"\"Build the GUI interface.\"\"\"
        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC
        )
        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_left_margin(6)
        self.textview.set_right_margin(6)
        self.textview.set_cursor_visible(False)
        self.buffer = self.textview.get_buffer()

        self.buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        self.buffer.create_tag("italic", style=Pango.Style.ITALIC)
        self.buffer.create_tag(
            "h1", weight=Pango.Weight.BOLD, scale=1.728  # Pango XX_LARGE
        )
        self.buffer.create_tag(
            "h2", weight=Pango.Weight.BOLD, scale=1.440  # Pango X_LARGE
        )
        self.buffer.create_tag(
            "h3", weight=Pango.Weight.BOLD, scale=1.200  # Pango LARGE
        )
        self.buffer.create_tag("h4", weight=Pango.Weight.BOLD)
        self.buffer.create_tag("h5", weight=Pango.Weight.BOLD)
        self.buffer.create_tag("h6", weight=Pango.Weight.BOLD)
        try:
            _lbl = Gtk.Label()
            _rgba = _lbl.get_style_context().get_color(Gtk.StateFlags.LINK)
            _link_color = "#{{:02x}}{{:02x}}{{:02x}}".format(
                int(_rgba.red * 255),
                int(_rgba.green * 255),
                int(_rgba.blue * 255),
            )
        except Exception:
            _link_color = "blue"
        self.buffer.create_tag(
            "link", foreground=_link_color, underline=Pango.Underline.SINGLE
        )
        self.buffer.create_tag(
            "gramps_link", foreground="purple", underline=Pango.Underline.SINGLE
        )
        self.buffer.create_tag(
            "align_center", justification=Gtk.Justification.CENTER
        )
        self.buffer.create_tag(
            "align_right", justification=Gtk.Justification.RIGHT
        )

        self.textview.connect("button-press-event", self._on_link_click)
        self._links = []

        scrolledwindow.add(self.textview)
        self.display_text()
        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def _on_link_click(self, view, event):
        \"\"\"Handle left-click on link regions.\"\"\"
        if event.button != 1:
            return False
        buf_x, buf_y = view.window_to_buffer_coords(
            Gtk.TextWindowType.TEXT, int(event.x), int(event.y)
        )
        result = view.get_iter_at_location(buf_x, buf_y)
        # GTK >= 3.20 returns (bool, iter); earlier returns iter directly
        _iter = result[1] if isinstance(result, tuple) else result
        offset = _iter.get_offset()
        for start_off, end_off, url in self._links:
            if start_off <= offset < end_off:
                {link_action}
                return True
        return False

{gramps_link_method}    def display_text(self):
        \"\"\"Display the content.\"\"\"
{body}

    def get_has_data(self, obj):
        \"\"\"Return True if the gramplet has data.\"\"\"
        return True
""")

    return "".join(parts)


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if not src.exists():
        print(f"Error: {src} not found", file=sys.stderr)
        sys.exit(1)

    text = src.read_text(encoding="utf-8")
    config, body = parse_front_matter(text)

    if "class" not in config:
        print(
            "Error: YAML front matter must include a 'class' field.",
            file=sys.stderr,
        )
        sys.exit(1)

    blocks = parse_markdown(body)

    # Validate all image paths and gramps: URLs at generation time.
    for block in blocks:
        if block["type"] == "block_image":
            check_image(block["path"], src)
        elif block["type"] == "icon_para":
            check_image(block["icon"], src)
        elif block["type"] == "heading" and block.get("icon"):
            check_image(block["icon"], src)
        elif block["type"] == "link" and block["url"].startswith("gramps:"):
            check_gramps_url(block["url"], src)

    code = generate(config, blocks)

    dst.write_text(code, encoding="utf-8")

    n_headings = sum(1 for b in blocks if b["type"] == "heading")
    n_paras = sum(1 for b in blocks if b["type"] == "paragraph")
    n_links = sum(1 for b in blocks if b["type"] == "link")
    n_bimgs = sum(1 for b in blocks if b["type"] == "block_image")
    n_iparas = sum(1 for b in blocks if b["type"] == "icon_para")
    print(
        f"Generated {dst}  "
        f"({n_headings} headings, {n_paras} paragraphs, {n_links} links"
        + (f", {n_bimgs} block images" if n_bimgs else "")
        + (f", {n_iparas} icon paragraphs" if n_iparas else "")
        + ")"
    )


if __name__ == "__main__":
    main()
