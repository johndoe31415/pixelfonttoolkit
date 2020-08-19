#	pixelfonttoolkit - Pixel font generation and handling tools.
#	Copyright (C) 2020-2020 Johannes Bauer
#
#	This file is part of pixelfonttoolkit.
#
#	pixelfonttoolkit is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pixelfonttoolkit is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pixelfonttoolkit; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import json
from .BaseAction import BaseAction
from .Font import Font

class ActionConvert(BaseAction):
	def _convert_ascii(self, f):
		print("# Font: %s, %d glyphs" % (self._font.name, len(self._font)), file = f)
		print(file = f)
		print_mode = "dots" if (self._font.colors == 2) else "values"
		for (glyphno, (codepoint, glyph)) in enumerate(self._font):
			print("# Glyph %d: \"%s\"" % (glyphno, codepoint), file = f)
			glyph.print_data(f, mode = print_mode)
			print(file = f)

	def _convert_bitfontmaker(self, f):
		bfmdata = {
			"name":				self._font.name or "",
			"copy":				"",
			"letterspace":		"64",
			"basefont_size":	"512",
			"basefont_left":	"62",
			"basefont_top":		"0",
			"basefont":			"Arial",
			"basefont2":		"",
		}
		for (codepoint, glyph) in self._font:
			fontdata = [ 0 ] * 16
			for (x, y) in glyph.iter_set_pixels():
				fontdata[y + 11 + glyph.yoffset] |= (1 << (x + 2 + glyph.xoffset))
			bfmdata[str(ord(codepoint))] = fontdata
		json.dump(bfmdata, f)
		f.write("\n")

	def _convert_python(self, f):
		print("from UDisplay import UDisplay", file = f)
		print(file = f)
		print("glyphs = {", file = f)
		for (codepoint, glyph) in self._font:
			if not self._args.no_optimize:
				glyph = glyph.optimize()
			bitmap = glyph.get_bitmap(mode = "ybit")
			if self._args.verbose >= 2:
				print(glyph)
				bitmap.print()
			glyph_data = ", ".join("0x%02x" % (x) for x in bitmap.data)
			print("	\"%s\": UDisplay.create_glyph(width = %d, height = %d, xoffset = %d, yoffset = %d, xadvance = %d, data = bytes((%s)))," % (codepoint, glyph.width, glyph.height, glyph.xoffset, glyph.yoffset, glyph.xadvance, glyph_data), file = f)
		print("}", file = f)

	def run(self):
		self._font = Font.load_from_file(self._args.font_filename)

		method_name = "_convert_" + self._args.format
		method = getattr(self, method_name)
		with open(self._args.outfile, "w") as f:
			method(f)
