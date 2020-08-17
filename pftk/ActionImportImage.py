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

import sys
import json
import collections
import PIL.Image
from .BaseAction import BaseAction
from .Font import Font
from .Glyph import Glyph

class ActionImportImage(BaseAction):
	_BoundingBox = collections.namedtuple("BoundingBox", [ "x", "y", "width", "height" ])

	def _pixel_set(self, x, y):
		pixel_no = x + (self._img.width * y)
		pixel = self._data[pixel_no]
		return pixel != (255, 255, 255)

	def _pixel_get_gray(self, x, y):
		pixel_no = x + (self._img.width * y)
		pixel = self._data[pixel_no]
		return round((pixel[0] + pixel[1] + pixel[2]) / 3)

	def _column_empty(self, x):
		for y in range(self._img.height):
			if self._pixel_set(x, y):
				return False
		return True

	def _find_horizontal_glyphs(self):
		glyphs = [ ]
		current_glyph = None
		for x in range(self._img.width):
			empty = self._column_empty(x)
			if (not empty) and (current_glyph is None):
				# Start of new glyph
				current_glyph = [ x, 1 ]
				glyphs.append(current_glyph)
			elif (not empty) and (current_glyph is not None):
				# Continuation of glyph
				current_glyph[1] += 1
			elif empty and (current_glyph is not None):
				# End of current glyph
				current_glyph = None

		for (x_start, width) in glyphs:
			yield self._BoundingBox(x = x_start, y = 0, width = width, height = self._img.height)

	def _create_glyph(self, codepoint, boundingbox):
		raw_data = bytearray()
		for glyph_y in range(boundingbox.height):
			y = boundingbox.y + glyph_y
			for glyph_x in range(boundingbox.width):
				x = boundingbox.x + glyph_x
				pixel = self._pixel_get_gray(x, y)
				raw_data.append(pixel)
		raw_data = bytes(raw_data)

		glyph = Glyph(codepoint = codepoint, width = boundingbox.width, height = boundingbox.height, xoffset = 0, yoffset = -boundingbox.height, xadvance = boundingbox.width + 1, raw_data = raw_data)
		return glyph

	def run(self):
		self._img = PIL.Image.open(self._args.png_image)
		if self._args.verbose >= 2:
			print("%s: %d x %d pixels" % (self._args.png_image, self._img.width, self._img.height))
		self._data = self._img.getdata()
		glyph_bbs = list(self._find_horizontal_glyphs())
		if self._args.verbose >= 2:
			print("Found %d glyphs: %s" % (len(glyph_bbs), str(glyph_bbs)))
		elif self._args.verbose >= 2:
			print("Found %d glyphs." % (len(glyph_bbs)))
		if len(glyph_bbs) != len(self._args.glyphs):
			print("Found %d glyphs in image, but specification for %d glyphs. Mismatch; terminating." % (len(glyph_bbs), len(self._args.glyphs)), file = sys.stderr)
			sys.exit(1)

		font = Font()
		for (codepoint, glyph_bb) in zip(self._args.glyphs, glyph_bbs):
			glyph = self._create_glyph(codepoint, glyph_bb)
			font.add_glyph(glyph)
		with open(self._args.outfile, "w") as f:
			json.dump(font.serialize(), f)
