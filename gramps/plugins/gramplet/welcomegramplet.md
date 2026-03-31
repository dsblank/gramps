---
class: WelcomeGramplet
description: Displays a welcome note to the user.
copyright:
  - 2007-2009  Douglas S. Blank <doug.blank@gmail.com>
  - 2020       Dave Scheipers
imports:
  - from gramps.gen.const import URL_WIKISTRING, URL_MANUAL_PAGE, URL_HOMEPAGE
  - from gramps.gen.const import WIKI_EXTRAPLUGINS
  - from gramps.gui.display import EXTENSION
vars:
  url_contact: "URL_HOMEPAGE + 'contact/'"
---

![](gramps:image:gramps.png|120|center)

## ![](gramps:icon:gramps-tree-list:22) Intro

**Gramps** is a software package designed for genealogical research.
Although similar to other genealogical programs, Gramps offers
some unique and powerful features.

- [Home Page]({URL_HOMEPAGE})

## ![](gramps:icon:gramps-person:22) Who makes Gramps?

Gramps is created by genealogists for genealogists, organized in
the Gramps Project. Gramps is an Open Source Software package,
which means you are free to make copies and distribute it to
anyone you like. It's developed and maintained by a worldwide
team of volunteers whose goal is to make Gramps powerful, yet
easy to use.

There is an active community of users available on the mailing
lists and Discourse forum to share ideas and techniques.

- [Gramps online manual](wiki_manual:)
- [Ask questions on gramps-users mailing list]({url_contact})
- [Gramps Discourse Forum](https://gramps.discourse.group/)

## ![](gramps:icon:gramps-pedigree:22) Getting Started

The first time Gramps is started all of the Views are blank. There
are very few menu options. A Family Tree is needed for any activity
to happen.

To create a new Family Tree (sometimes called 'database') select
"Family Trees" from the menu, pick "Manage Family Trees", press
"New" and name your Family Tree. "Load Family Tree" to make the
tree active and ready to accept data by entering your first
family, or importing a family tree. For more details, please
read the information at the links below.

- [Start with Genealogy and Gramps](wiki:Start_with_Genealogy)

## ![](gramps:icon:gramps-relation:22) Enter your first Family

You will now want to start entering your first Family and that
starts with the first Person.

Switch to the "People" view and from the menu clicking "Add" and then
clicking "Person" (or using the [+] icon) will bring up the window
to enter a person. Entering the basic information and saving the
record gives you a starting point. Select this Person's record and
now switch to the "Relationships" view.

With this first person, all of the menu options and icon functions
have become available. Spend some time moving your mouse over the
icons. As your cursor passes over an icon, a message will appear
telling you the icon's function. The same is true for any of the
edit windows. Moving the mouse cursor over an item will tell you
what it will do.

You can now create families by adding parents, a spouse and children.
Once started, you will be able to add Events to People and Families.
You can provide Sources and Citations to provide documentation for
your entries.

As you start using Gramps, you will find that information can be
entered from all the various Views. There are multiple ways of
doing most activities in Gramps. The flexibility allows you to
choose which fits your work style.

- [Entering and editing data (brief)](wiki_manual:_-_Entering_and_editing_data:_brief)

## ![](gramps:image:gramps-import.png) Importing a Family Tree

To import a Family Tree from another program first create
a GEDCOM (or other data) file from the previous program.

Once you have created a new Gramps database file, use the "Import"
option under the "Family Trees" menu to import the GEDCOM data.

- [Import from another genealogy program](wiki:Import_from_another_genealogy_program)

## ![](gramps:icon:gramps-gramplet:22) Dashboard View

You are currently reading from the "Dashboard" view, where you can
add your own gramplets. You can also add gramplets to any view by
adding a sidebar and/or bottombar, and right-clicking to the
right of the tab.

![](gramps:icon:gramps-config:22) You can click the configuration icon in the toolbar to add additional columns, while right-click on the background allows to add gramplets.

![](gramps:icon:gramps-config:22) You can also drag the Properties button to reposition the gramplet on this page, and detach the gramplet to float above Gramps.

- [Gramps View Categories](wiki_manual:_-_Categories)

## ![](gramps:icon:gramps-gramplet:22) Addons and "Gramplets"

There are many Addons or "Gramplets" that are available to assist you
in data entry and visualizing your family tree. Many of these tools
are already available to you. Many more are available to download
and install.

- [Addons and "Gramplets"](wiki:{WIKI_EXTRAPLUGINS})

## ![](gramps:icon:gramps-tree-group:22) Example Database

Want to see Gramps in use? Create and Import the Example database.

Create a new Family Tree as described above. We suggest that you name
the Family Tree "EXAMPLE".

Import the Gramps file example.gramps.

Follow the instructions for the location of the file stored with
the Gramps program.

- ~[Example.gramps](wiki:Example.gramps)
