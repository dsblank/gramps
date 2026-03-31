# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
# Copyright (C) 2020       Dave Scheipers
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
from gramps.gen.const import URL_WIKISTRING, URL_MANUAL_PAGE, URL_HOMEPAGE
from gramps.gen.const import WIKI_EXTRAPLUGINS
from gramps.gui.display import EXTENSION
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
# WelcomeGramplet
#
# ------------------------------------------------------------------------


class WelcomeGramplet(Gramplet):
    """Displays a welcome note to the user."""

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
                display_url(url)
                return True
        return False

    def display_text(self):
        """Display the content."""
        url_contact = URL_HOMEPAGE + "contact/"

        buf = self.buffer
        buf.set_text("")
        links = []

        _ins_image(buf, "gramps:image:gramps.png", width=120, align="center")
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-tree-list:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Intro"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "**Gramps** is a software package designed for genealogical research."
                " Although similar to other genealogical programs, Gramps offers some"
                " unique and powerful features."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Home Page"), URL_HOMEPAGE)
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-person:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Who makes Gramps?"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "Gramps is created by genealogists for genealogists, organized in the"
                " Gramps Project. Gramps is an Open Source Software package, which"
                " means you are free to make copies and distribute it to anyone you"
                " like. It's developed and maintained by a worldwide team of"
                " volunteers whose goal is to make Gramps powerful, yet easy to use."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "There is an active community of users available on the mailing lists"
                " and Discourse forum to share ideas and techniques."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _("Gramps online manual"), wiki("", manual=True))
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf, links, _("Ask questions on gramps-users mailing list"), url_contact
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf, links, _("Gramps Discourse Forum"), "https://gramps.discourse.group/"
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-pedigree:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Getting Started"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "The first time Gramps is started all of the Views are blank. There"
                " are very few menu options. A Family Tree is needed for any activity"
                " to happen."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "To create a new Family Tree (sometimes called 'database') select"
                ' "Family Trees" from the menu, pick "Manage Family Trees", press'
                ' "New" and name your Family Tree. "Load Family Tree" to make the tree'
                " active and ready to accept data by entering your first family, or"
                " importing a family tree. For more details, please read the"
                " information at the links below."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Start with Genealogy and Gramps"),
            wiki("Start_with_Genealogy"),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-relation:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Enter your first Family"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "You will now want to start entering your first Family and that"
                " starts with the first Person."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                'Switch to the "People" view and from the menu clicking "Add" and'
                ' then clicking "Person" (or using the [+] icon) will bring up the'
                " window to enter a person. Entering the basic information and saving"
                " the record gives you a starting point. Select this Person's record"
                ' and now switch to the "Relationships" view.'
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "With this first person, all of the menu options and icon functions"
                " have become available. Spend some time moving your mouse over the"
                " icons. As your cursor passes over an icon, a message will appear"
                " telling you the icon's function. The same is true for any of the"
                " edit windows. Moving the mouse cursor over an item will tell you"
                " what it will do."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "You can now create families by adding parents, a spouse and"
                " children. Once started, you will be able to add Events to People and"
                " Families. You can provide Sources and Citations to provide"
                " documentation for your entries."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "As you start using Gramps, you will find that information can be"
                " entered from all the various Views. There are multiple ways of doing"
                " most activities in Gramps. The flexibility allows you to choose"
                " which fits your work style."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Entering and editing data (brief)"),
            wiki("_-_Entering_and_editing_data:_brief", manual=True),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:image:gramps-import.png")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Importing a Family Tree"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "To import a Family Tree from another program first create a GEDCOM"
                " (or other data) file from the previous program."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                'Once you have created a new Gramps database file, use the "Import"'
                ' option under the "Family Trees" menu to import the GEDCOM data.'
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf,
            links,
            _("Import from another genealogy program"),
            wiki("Import_from_another_genealogy_program"),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-gramplet:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Dashboard View"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                'You are currently reading from the "Dashboard" view, where you can'
                " add your own gramplets. You can also add gramplets to any view by"
                " adding a sidebar and/or bottombar, and right-clicking to the right"
                " of the tab."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-config:22")
        buf.insert(buf.get_end_iter(), " ")
        _render_inline(
            buf,
            _(
                "You can click the configuration icon in the toolbar to add"
                " additional columns, while right-click on the background allows to"
                " add gramplets."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-config:22")
        buf.insert(buf.get_end_iter(), " ")
        _render_inline(
            buf,
            _(
                "You can also drag the Properties button to reposition the gramplet"
                " on this page, and detach the gramplet to float above Gramps."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(
            buf, links, _("Gramps View Categories"), wiki("_-_Categories", manual=True)
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-gramplet:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _('Addons and "Gramplets"'))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                'There are many Addons or "Gramplets" that are available to assist'
                " you in data entry and visualizing your family tree. Many of these"
                " tools are already available to you. Many more are available to"
                " download and install."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, _('Addons and "Gramplets"'), wiki(WIKI_EXTRAPLUGINS))
        buf.insert(buf.get_end_iter(), "\n\n")

        _ins_image(buf, "gramps:icon:gramps-tree-group:22")
        buf.insert(buf.get_end_iter(), " ")
        start = buf.get_char_count()
        buf.insert(buf.get_end_iter(), _("Example Database"))
        buf.apply_tag_by_name("h2", buf.get_iter_at_offset(start), buf.get_end_iter())
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf, _("Want to see Gramps in use? Create and Import the Example database.")
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "Create a new Family Tree as described above. We suggest that you"
                ' name the Family Tree "EXAMPLE".'
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(buf, _("Import the Gramps file example.gramps."))
        buf.insert(buf.get_end_iter(), "\n\n")

        _render_inline(
            buf,
            _(
                "Follow the instructions for the location of the file stored with the"
                " Gramps program."
            ),
        )
        buf.insert(buf.get_end_iter(), "\n\n")

        buf.insert(buf.get_end_iter(), "  \u2022 ")
        _ins_link(buf, links, "Example.gramps", wiki("Example.gramps"))
        buf.insert(buf.get_end_iter(), "\n\n")

        self._links = links

    def get_has_data(self, obj):
        """Return True if the gramplet has data."""
        return True
