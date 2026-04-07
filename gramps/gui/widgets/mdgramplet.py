# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024  Douglas S. Blank <doug.blank@gmail.com>
#
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
gramps.gui.widgets.mdgramplet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MarkdownGramplet — base class for gramplets backed by a .md file.

Subclass and set the ``md_file`` class attribute to the basename of the
markdown file (without the .md extension).  The file is resolved relative to
the subclass's own source file so that each plugin can ship its own .md:

    class WelcomeGramplet(MarkdownGramplet):
        md_file = "welcomegramplet"
"""

import os
import sys

from gi.repository import Gtk

from gramps.gen.plug import Gramplet
from gramps.gen.utils.markdown import parse_front_matter
from gramps.gui.display import display_url
from gramps.gui.widgets.markdown_render import (
    _handle_gramps_link,
    load_md,
    render_md,
    setup_tags,
)


class MarkdownGramplet(Gramplet):
    """Gramplet base class that renders content from a .md file at runtime.

    Subclasses set ``md_file`` to the basename of the markdown source file
    (no extension).  The file is looked up relative to the subclass module's
    directory, with locale-aware fallback (e.g. ``welcome.fr_FR.md``).
    """

    md_file = None  # Override in subclass, e.g. "welcomegramplet"

    # ── Gramplet lifecycle ────────────────────────────────────────────────────

    def init(self):
        self.gui.WIDGET = self._build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def get_has_data(self, obj):
        return True

    # ── GUI construction ──────────────────────────────────────────────────────

    def _build_gui(self):
        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.textview = Gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_left_margin(6)
        self.textview.set_right_margin(6)
        self.textview.set_cursor_visible(False)

        self.buffer = self.textview.get_buffer()
        setup_tags(self.buffer)

        self._links = []
        self.textview.connect("button-press-event", self._on_link_click)

        scrolledwindow.add(self.textview)
        self._render()

        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render(self):
        """Load the .md file, evaluate vars, and render into the buffer."""
        module = sys.modules[type(self).__module__]
        plugin_dir = os.path.dirname(os.path.abspath(module.__file__))
        text = load_md(plugin_dir, self.md_file)
        config, _body = parse_front_matter(text)
        vars = self._eval_vars(config)
        self._links = []
        render_md(
            text,
            self.buffer,
            self._links,
            dbstate=self.dbstate,
            uistate=self.uistate,
            vars=vars,
        )

    def _eval_vars(self, config):
        """Build a vars dict from front-matter imports and vars expressions.

        ``imports:`` lines are exec'd to populate a namespace; ``vars:``
        expressions are eval'd inside that same namespace.  The resulting
        dict (minus dunder keys) is returned so that both imported names
        (e.g. ``URL_HOMEPAGE``) and derived names (e.g. ``url_contact``)
        are available for ``{VARNAME}`` substitution in URLs.
        """
        ns = {}
        for stmt in config.get("imports", []):
            try:
                exec(stmt, ns)  # noqa: S102
            except Exception:
                pass
        for name, expr in config.get("vars", {}).items():
            try:
                ns[name] = eval(expr, ns)  # noqa: S307
            except Exception:
                ns[name] = expr
        return {k: v for k, v in ns.items() if not k.startswith("__")}

    # ── Link click handler ────────────────────────────────────────────────────

    def _on_link_click(self, view, event):
        """Dispatch a left-click on a link region to a URL or Gramps action."""
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
                if url.startswith("gramps:"):
                    _handle_gramps_link(url, self.dbstate, self.uistate)
                else:
                    display_url(url)
                return True
        return False
