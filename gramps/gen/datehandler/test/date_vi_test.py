# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Doug Blank
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Tests for the Vietnamese date handler (parser and displayer)."""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.lib.date import Date
from gramps.gen.datehandler._date_vi import DateParserVI, DateDisplayVI


class TestDateParserVI(unittest.TestCase):
    """Tests for DateParserVI — Vietnamese-language date input."""

    def setUp(self):
        """Create parser instance."""
        self.dp = DateParserVI()

    # --- Vietnamese Lunar month names ---

    def test_thang_gieng(self):
        """'Tháng Giêng' (month 1) parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng Giêng 1 2024")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_thang_hai(self):
        """'Tháng Hai' (month 2) parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng Hai 15 2023")
        self.assertEqual(result, (15, 2, 2023, False))

    def test_thang_muoi_mot(self):
        """'Tháng Mười Một' (month 11) parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng Mười Một 1 2022")
        self.assertEqual(result, (1, 11, 2022, False))

    def test_thang_chap(self):
        """'Tháng Chạp' (month 12) parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng Chạp 29 2024")
        self.assertEqual(result, (29, 12, 2024, False))

    def test_numeric_thang(self):
        """'Tháng 5' (numeric shorthand) parses correctly."""
        result = self.dp._parse_vietnamese_lunar("Tháng 5 10 2025")
        self.assertEqual(result, (10, 5, 2025, False))

    # --- Leap months ---

    def test_nhuan_thang_tu(self):
        """'Nhuận Tháng Tư' (leap month 4) parses to month 104."""
        result = self.dp._parse_vietnamese_lunar("Nhuận Tháng Tư 1 2020")
        self.assertEqual(result, (1, 104, 2020, False))

    def test_nhuan_thang_numeric(self):
        """'Nhuận Tháng 4' (numeric leap month) parses to month 104."""
        result = self.dp._parse_vietnamese_lunar("Nhuận Tháng 4 1 2020")
        self.assertEqual(result, (1, 104, 2020, False))

    def test_nhuan_thang_chap(self):
        """'Nhuận Tháng Chạp' (leap month 12) parses to month 112."""
        result = self.dp._parse_vietnamese_lunar("Nhuận Tháng Chạp 1 2033")
        self.assertEqual(result, (1, 112, 2033, False))

    # --- ISO numeric fallback ---

    def test_iso_numeric(self):
        """ISO numeric YYYY-MM-DD parses correctly."""
        result = self.dp._parse_vietnamese_lunar("2024-1-1")
        self.assertEqual(result, (1, 1, 2024, False))

    def test_iso_year_only(self):
        """ISO year-only parses correctly."""
        result = self.dp._parse_vietnamese_lunar("2024-0-0")
        self.assertEqual(result, (0, 0, 2024, False))

    def test_unrecognized_returns_empty(self):
        """Unrecognized text returns Date.EMPTY."""
        result = self.dp._parse_vietnamese_lunar("not a date")
        self.assertEqual(result, Date.EMPTY)

    # --- calendar_to_int ---

    def test_am_lich_in_calendar_to_int(self):
        """'âm lịch' maps to CAL_VIETNAMESE_LUNAR."""
        self.assertEqual(self.dp.calendar_to_int["âm lịch"], Date.CAL_VIETNAMESE_LUNAR)

    def test_am_lich_ascii_in_calendar_to_int(self):
        """'am lich' (ASCII fallback) maps to CAL_VIETNAMESE_LUNAR."""
        self.assertEqual(self.dp.calendar_to_int["am lich"], Date.CAL_VIETNAMESE_LUNAR)

    # --- modifier_to_int ---

    def test_modifier_truoc(self):
        """'trước' maps to MOD_BEFORE."""
        self.assertEqual(self.dp.modifier_to_int["trước"], Date.MOD_BEFORE)

    def test_modifier_sau(self):
        """'sau' maps to MOD_AFTER."""
        self.assertEqual(self.dp.modifier_to_int["sau"], Date.MOD_AFTER)

    def test_modifier_khoang(self):
        """'khoảng' maps to MOD_ABOUT."""
        self.assertEqual(self.dp.modifier_to_int["khoảng"], Date.MOD_ABOUT)


class TestDateDisplayVI(unittest.TestCase):
    """Tests for DateDisplayVI — Vietnamese date output."""

    def setUp(self):
        """Create displayer instance."""
        self.dd = DateDisplayVI()

    def _make_date(self, year, month, day):
        """Return a Vietnamese Lunar Date."""
        d = Date()
        d.set(calendar=Date.CAL_VIETNAMESE_LUNAR, value=(day, month, year, False))
        return d

    def test_iso_format(self):
        """Format 0 (ISO) returns ISO string."""
        self.dd.format = 0
        d = self._make_date(2024, 1, 1)
        result = self.dd._display_vietnamese_lunar(d.get_dmy(get_slash=True))
        self.assertIn("2024", result)
        self.assertIn("1", result)

    def test_numeric_format_year_only(self):
        """Format 1: year-only date shows 'Năm YYYY'."""
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar((0, 0, 2024, False))
        self.assertEqual(result, "Năm 2024")

    def test_numeric_format_year_month(self):
        """Format 1: year + month shows month name."""
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar((0, 1, 2024, False))
        self.assertIn("Tháng Giêng", result)
        self.assertIn("2024", result)

    def test_numeric_format_full_date(self):
        """Format 1: full date includes year, month name, and day."""
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar((15, 1, 2024, False))
        self.assertIn("Tháng Giêng", result)
        self.assertIn("2024", result)
        self.assertIn("15", result)

    def test_can_chi_format(self):
        """Format 2: year is displayed as Can-Chi name."""
        self.dd.format = 2
        result = self.dd._display_vietnamese_lunar((1, 1, 2024, False))
        self.assertIn("Giáp Thìn", result)

    def test_leap_month_uses_iso(self):
        """Leap months always fall back to ISO regardless of format."""
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar((1, 104, 2020, False))
        self.assertIn("104", result)

    def test_thang_chap_display(self):
        """Month 12 (Tháng Chạp) is displayed correctly."""
        self.dd.format = 1
        result = self.dd._display_vietnamese_lunar((1, 12, 2024, False))
        self.assertIn("Tháng Chạp", result)


class TestVietnameseModifierParsing(unittest.TestCase):
    """Tests for modifier parsing and display in the Vietnamese date handler."""

    def setUp(self):
        """Create parser and displayer instances."""
        self.dp = DateParserVI()
        self.dd = DateDisplayVI()

    def _parse(self, text):
        """Parse a date string and return the Date object."""
        return self.dp.parse(text)

    # --- modifier_to_int ---

    def test_truoc_in_modifier_to_int(self):
        """'trước' is registered as MOD_BEFORE."""
        self.assertEqual(self.dp.modifier_to_int["trước"], Date.MOD_BEFORE)

    def test_sau_in_modifier_to_int(self):
        """'sau' is registered as MOD_AFTER."""
        self.assertEqual(self.dp.modifier_to_int["sau"], Date.MOD_AFTER)

    def test_khoang_in_modifier_to_int(self):
        """'khoảng' is registered as MOD_ABOUT."""
        self.assertEqual(self.dp.modifier_to_int["khoảng"], Date.MOD_ABOUT)

    # --- parser: modifier + bare year ---

    def test_parse_truoc_year(self):
        """'trước 2000' parses as MOD_BEFORE year=2000."""
        d = self._parse("trước 2000")
        self.assertEqual(d.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d.get_year(), 2000)

    def test_parse_sau_year(self):
        """'sau 1949' parses as MOD_AFTER year=1949."""
        d = self._parse("sau 1949")
        self.assertEqual(d.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d.get_year(), 1949)

    def test_parse_khoang_year(self):
        """'khoảng 1850' parses as MOD_ABOUT year=1850."""
        d = self._parse("khoảng 1850")
        self.assertEqual(d.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d.get_year(), 1850)

    # --- display: modifier strings have trailing space ---

    def test_display_truoc_has_trailing_space(self):
        """MOD_BEFORE display string ends with a space (prefix convention)."""
        mod_str = self.dd._mod_str[Date.MOD_BEFORE]
        self.assertTrue(mod_str.endswith(" "), repr(mod_str))

    def test_display_sau_has_trailing_space(self):
        """MOD_AFTER display string ends with a space (prefix convention)."""
        mod_str = self.dd._mod_str[Date.MOD_AFTER]
        self.assertTrue(mod_str.endswith(" "), repr(mod_str))

    def test_display_khoang_has_trailing_space(self):
        """MOD_ABOUT display string ends with a space (prefix convention)."""
        mod_str = self.dd._mod_str[Date.MOD_ABOUT]
        self.assertTrue(mod_str.endswith(" "), repr(mod_str))

    # --- display: modifier appears BEFORE the date ---

    def test_display_before_is_prefix(self):
        """'trước' appears before '2000' in display output."""
        d = Date()
        d.set(modifier=Date.MOD_BEFORE, value=(0, 0, 2000, False))
        result = self.dd.display(d)
        self.assertIn("trước", result)
        self.assertLess(result.index("trước"), result.index("2000"))

    def test_display_after_is_prefix(self):
        """'sau' appears before '1949' in display output."""
        d = Date()
        d.set(modifier=Date.MOD_AFTER, value=(0, 0, 1949, False))
        result = self.dd.display(d)
        self.assertIn("sau", result)
        self.assertLess(result.index("sau"), result.index("1949"))

    # --- round-trips ---

    def test_roundtrip_before(self):
        """Display then re-parse 'before 2000' round-trips correctly."""
        d = Date()
        d.set(modifier=Date.MOD_BEFORE, value=(0, 0, 2000, False))
        displayed = self.dd.display(d)
        d2 = self._parse(displayed)
        self.assertEqual(d2.get_modifier(), Date.MOD_BEFORE)
        self.assertEqual(d2.get_year(), 2000)

    def test_roundtrip_after(self):
        """Display then re-parse 'after 1949' round-trips correctly."""
        d = Date()
        d.set(modifier=Date.MOD_AFTER, value=(0, 0, 1949, False))
        displayed = self.dd.display(d)
        d2 = self._parse(displayed)
        self.assertEqual(d2.get_modifier(), Date.MOD_AFTER)
        self.assertEqual(d2.get_year(), 1949)

    def test_roundtrip_about(self):
        """Display then re-parse 'about 1850' round-trips correctly."""
        d = Date()
        d.set(modifier=Date.MOD_ABOUT, value=(0, 0, 1850, False))
        displayed = self.dd.display(d)
        d2 = self._parse(displayed)
        self.assertEqual(d2.get_modifier(), Date.MOD_ABOUT)
        self.assertEqual(d2.get_year(), 1850)


if __name__ == "__main__":
    unittest.main()
