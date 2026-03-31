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
from gramps.gen.plug import Gramplet
from gramps.gui.display import display_url
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
# ------------------------------------------------------------------------
#
# Runtime helpers  (edit the .md source, not this generated file)
#
# ------------------------------------------------------------------------
from gramps.gui.widgets.markdown_render import (
    _ins_image,
    _ins_link,
    _render_inline,
    wiki,
)

# ------------------------------------------------------------------------
#
# TestGramplet
#
# ------------------------------------------------------------------------


class TestGramplet(Gramplet):
    """Demonstrates Gramps object links — edit, navigate, and switch views."""

    def init(self):
        self.gui.WIDGET = self.build_gui()
        self.gui.get_container_widget().remove(self.gui.textview)
        self.gui.get_container_widget().add(self.gui.WIDGET)
        self.gui.WIDGET.show()

    def build_gui(self):
        """Build the GUI interface."""
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
            _link_color = "#{:02x}{:02x}{:02x}".format(
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
        self.buffer.create_tag("align_center", justification=Gtk.Justification.CENTER)
        self.buffer.create_tag("align_right", justification=Gtk.Justification.RIGHT)

        self.textview.connect("button-press-event", self._on_link_click)
        self._links = []

        scrolledwindow.add(self.textview)
        self.display_text()
        top.pack_start(scrolledwindow, True, True, 0)
        top.show_all()
        return top

    def _on_link_click(self, view, event):
        """Handle left-click on link regions."""
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
                    self._handle_gramps_link(url)
                else:
                    display_url(url)
                return True
        return False

    def _handle_gramps_link(self, url):
        """Dispatch a gramps: scheme URL to the appropriate Gramps action."""
        from gramps.gui.widgets.markdown_render import _handle_gramps_link as _dispatch

        _dispatch(url, self.dbstate, self.uistate)

    def display_text(self):
        """Display the content."""
        buf = self.buffer
        buf.set_text("")
        links = []

        _ins_image(buf, "gramps:icon:gramps-gramplet:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Gramps Object Links"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "**Purple links** interact directly with your open family tree"
                " database. They open editors, set the active record, or switch views"
                " — no browser needed."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-person:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Edit Links"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf, _("Open an editor dialog for a specific record by Gramps ID.")
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Edit person I0001"),
            "gramps:edit:Person:I0001",
            "gramps_link",
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Edit family F0001"),
            "gramps:edit:Family:F0001",
            "gramps_link",
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf, links, _("Edit event E0001"), "gramps:edit:Event:E0001", "gramps_link"
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf, links, _("Edit place P0001"), "gramps:edit:Place:P0001", "gramps_link"
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Edit source S0001"),
            "gramps:edit:Source:S0001",
            "gramps_link",
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-pedigree:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Navigate Links"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _("Make a record active in the current view without opening an editor."),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Go to person I0001"),
            "gramps:nav:Person:I0001",
            "gramps_link",
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Go to family F0001"),
            "gramps:nav:Family:F0001",
            "gramps_link",
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-tree-list:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("View Links"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(buf, _("Switch to a different view category."))
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("People"), "gramps:view:people", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Families"), "gramps:view:families", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Events"), "gramps:view:events", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Places"), "gramps:view:places", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Geography"), "gramps:view:geography", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Dashboard"), "gramps:view:dashboard", "gramps_link")
        buf.insert(buf.get_end_iter(), "\n\n")

        self._links = links

    def get_has_data(self, obj):
        """Return True if the gramplet has data."""
        return True
