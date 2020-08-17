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
import collections
from .Glyph import Glyph

class Font(object):
	_TextExtents = collections.namedtuple("TextExtents", [ "width", "height", "height_above_baseline", "height_below_baseline", "missing_glyphs", "missing_glyph_count" ])

	def __init__(self, name = None, size = None, antialiasing = None):
		self._name = name
		self._size = size
		self._antialiasing = antialiasing
		self._glyphs = { }

	@property
	def name(self):
		return self._name

	@property
	def size(self):
		return self._size

	@property
	def antialiasing(self):
		return self._antialiasing

	@property
	def colors(self):
		return max(glyph.colors for glyph in self._glyphs.values())

	def export(self, export_cmd):
		codepoint = ord(export_cmd.glyph)
		glyph = self._glyphs[codepoint]
		glyph.write_to_pnm(export_cmd)

	def replace_glyph(self, glyph):
		self._glyphs[glyph.codepoint] = glyph

	def add_glyph(self, glyph):
		if glyph.codepoint in self._glyphs:
			raise Exception("Glyph codepoint %d already present in font." % (glyph.codepoint))
		self.replace_glyph(glyph)

	def dump(self):
		for (codepoint, glyph) in sorted(self._glyphs.items()):
			print(glyph)

	@property
	def max_glyph_width(self):
		return max(glyph.width for glyph in self._glyphs.values())

	@property
	def max_glyph_height(self):
		return max(glyph.height for glyph in self._glyphs.values())

#	def enumerate_glyphs(self):
#		for (charindex, (codepoint, glyph)) in enumerate(self):
#			glyph.charindex = charindex
#
#	def charindex_to_glyph_mapping(self):
#		cp_diff = [ (codepoint, codepoint - charindex) for (charindex, (codepoint, glyph)) in enumerate(self) ]
#		ranges = [ ]
#		for (codepoint, difference) in cp_diff:
#			if (len(ranges) == 0) or (difference != ranges[-1][2]):
#				ranges.append([ codepoint, codepoint, difference ])
#			else:
#				ranges[-1][1] = codepoint
#		return ranges

	def serialize(self):
		return {
			"metadata": {
				"name":			self.name,
				"size":			self.size,
				"antialiasing":	self.antialiasing,
				"colors":		self.colors,
			},
			"glyphs": [ glyph.serialize() for glyph in self._glyphs.values() ],
		}

	@classmethod
	def deserialize(cls, font_data):
		meta = font_data.get("metadata", { })
		font = cls(name = meta.get("name"), size = meta.get("size"), antialiasing = meta.get("antialiasing"))
		for glyph_data in font_data["glyphs"]:
			glyph = Glyph.deserialize(glyph_data)
			font.add_glyph(glyph)
		return font

	@classmethod
	def load_from_file(cls, filename):
		with open(filename) as f:
			font_data = json.load(f)
		font = cls.deserialize(font_data)
		return font

	def save_to_file(self, filename):
		with open(filename, "w") as f:
			json.dump(self.serialize(), f)
			print(file = f)

	def get_text_extents(self, text):
		missing_glyphs = set()
		missing_glyph_count = 0
		posx = 0
		max_y_above = 0
		max_y_below = 0
		for char in text:
			glyph = self._glyphs.get(char)
			if glyph is None:
				missing_glyph_count += 1
				missing_glyphs.add(char)
			else:
				for (x, y) in glyph.iter_set_pixels(mode = "virtual"):
					if y <= 0:
						# Above baseline
						max_y_above = max(max_y_above, abs(y))
					else:
						# Below baseline
						max_y_below = max(max_y_below, y)
				posx += glyph.xadvance
		return self._TextExtents(width = posx, height = max_y_above + max_y_below, height_above_baseline = max_y_above, height_below_baseline = max_y_below, missing_glyphs = missing_glyphs, missing_glyph_count = missing_glyph_count)

	def write(self, text, posx, posy, callback_put_pixel = None, callback_missing_glyph = None, callback_start_draw = None, callback_end_draw = None):
		for char in text:
			glyph = self._glyphs.get(char)
			if glyph is None:
				if callback_missing_glyph is not None:
					callback_missing_glyph()
			else:
				if callback_start_draw is not None:
					callback_start_draw(posx, posy)
				for (x, y) in glyph.iter_set_pixels(mode = "virtual", ref = (posx, posy)):
					if callback_put_pixel is not None:
						callback_put_pixel(x, y)
				posx += glyph.xadvance
				if callback_end_draw is not None:
					callback_end_draw(posx, posy)

	def get_glyph(self, codepoint):
		return self._glyphs.get(codepoint)

	def get_all_glyphs(self):
		return self._glyphs.values()

	def __iter__(self):
		return iter(sorted(self._glyphs.items()))

	def __len__(self):
		return len(self._glyphs)

	def __str__(self):
		return "Font<%d glyphs>" % (len(self))
