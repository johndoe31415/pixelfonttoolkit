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

import collections

class BitmapGlyph(object):
	def __init__(self, glyph, mode = "xbit"):
		assert(mode in [ "xbit", "ybit" ])
		self._glyph = glyph
		self._mode = mode
		if self._mode == "xbit":
			self._width = (self._glyph.width + 7) // 8
			self._height = self._glyph.height
		else:
			self._width = self._glyph.width
			self._height = (self._glyph.height + 7) // 8
		self._data = bytearray(self._width * self._height)

	@classmethod
	def create_from_glyph(cls, glyph, threshold, mode = "xbit"):
		bitmap = BitmapGlyph(glyph = glyph, mode = mode)
		for (x, y) in glyph.iter_set_pixels(threshold = threshold):
			bitmap.set_pixel(x, y)
		return bitmap

	@property
	def glyph(self):
		return self._glyph

	@property
	def width(self):
		return self._width

	@property
	def height(self):
		return self._height

	@property
	def data(self):
		return bytes(self._data)

	def _get_offset_bit(self, x, y):
		assert(0 <= x < self.glyph.width)
		assert(0 <= y < self.glyph.height)
		if self._mode == "xbit":
			byte_offset = (x // 8) + (y * self._width)
			bit_offset = x % 8
		elif self._mode == "ybit":
			byte_offset = (y // 8) + (x * self._height)
			bit_offset = y % 8
		else:
			raise NotImplementedError(self._mode)
		return (byte_offset, bit_offset)

	def get_pixel(self, x, y):
		(byte_offset, bit_offset) = self._get_offset_bit(x, y)
		return ((self._data[byte_offset] >> bit_offset) & 1) != 0

	def set_pixel(self, x, y):
		(byte_offset, bit_offset) = self._get_offset_bit(x, y)
		self._data[byte_offset] |= (1 << bit_offset)

	def clear_pixel(self, x, y):
		(byte_offset, bit_offset) = self._get_offset_bit(x, y)
		self._data[byte_offset] &= ~(1 << bit_offset)

	def set_pixel_to(self, x, y, value):
		if value:
			self.set_pixel(x, y)
		else:
			self.clear_pixel(x, y)

	def print(self):
		for y in range(self._glyph.height):
			line = ""
			for x in range(self._glyph.width):
				if self.get_pixel(x, y):
					line += "⬤ "
				else:
					line += "  "
			print(line)
		print("-" * 120)

class Glyph(object):
	_GlyphExtents = collections.namedtuple("GlyphExtents", [ "minx", "maxx", "miny", "maxy" ])

	def __init__(self, codepoint, width, height, xoffset, yoffset, xadvance, raw_data):
		assert(isinstance(raw_data, bytes))
		assert(len(raw_data) == width * height)
		self._codepoint = codepoint
		self._width = width
		self._height = height
		self._xoffset = xoffset
		self._yoffset = yoffset
		self._xadvance = xadvance
		self._raw_data = bytes(raw_data)

	@property
	def colors(self):
		return len(set(self._raw_data))

	@property
	def codepoint(self):
		return self._codepoint

	@property
	def width(self):
		return self._width

	@property
	def height(self):
		return self._height

	@property
	def xoffset(self):
		return self._xoffset

	@property
	def yoffset(self):
		return self._yoffset

	@property
	def xadvance(self):
		return self._xadvance

	@property
	def raw_data(self):
		return self._raw_data

	def get_pixel(self, x, y):
		assert(0 <= x < self.width)
		assert(0 <= y < self.height)
		return self._raw_data[(y * self.width) + x]

	def iter_set_pixels(self, threshold = 255, mode = "real", ref = (0, 0)):
		assert(mode in [ "real", "virtual" ])
		for y in range(self.height):
			for x in range(self.width):
				pixel = self.get_pixel(x, y)
				if pixel < threshold:
					# Pixel is set
					if mode == "real":
						yield (x + ref[0], y + ref[1])
					elif mode == "virtual":
						yield (x + self.xoffset + ref[0], y + self.yoffset + ref[1])
					else:
						raise NotImplementedError(mode)

	def iter_area(self, xoffset, yoffset, width, height):
		assert(width >= 0)
		assert(height >= 0)
		if (width == 0) or (height == 0):
			return
		assert(xoffset + width <= self.width)
		assert(yoffset + height <= self.height)
		for y in range(height):
			for x in range(width):
				pixel = self.get_pixel(x + xoffset, y + yoffset)
				yield (x + xoffset, y + yoffset, pixel)

	def find_extents(self):
		(minx, maxx, miny, maxy) = (None, None, None, None)
		for (x, y) in self.iter_set_pixels(threshold = 255):
			if (minx is None) or (x < minx):
				minx = x
			if (maxx is None) or (x > maxx):
				maxx = x
			if (miny is None) or (y < miny):
				miny = y
			if (maxy is None) or (y > maxy):
				maxy = y
		return self._GlyphExtents(minx = minx, maxx = maxx, miny = miny, maxy = maxy)

	def optimize(self):
		extents = self.find_extents()
		if extents.minx is not None:
			new_width = extents.maxx - extents.minx + 1
			new_height = extents.maxy - extents.miny + 1
			raw_data = bytearray(new_width * new_height)
			for (x, y, pixel) in self.iter_area(extents.minx, extents.miny, new_width, new_height):
				offset = ((y - extents.miny) * new_width) + (x - extents.minx)
				raw_data[offset] = pixel
			raw_data = bytes(raw_data)
			new_glyph = Glyph(codepoint = self.codepoint, width = new_width, height = new_height, xoffset = self.xoffset + extents.minx, yoffset = self.yoffset + extents.miny, xadvance = self.xadvance, raw_data = raw_data)
		else:
			raise NotImplementedError("optimizing completely empty glyph")
		return new_glyph

	def get_bitmap(self, threshold = 255, mode = "xbit"):
		bitmap = BitmapGlyph.create_from_glyph(glyph = self, threshold = threshold, mode = mode)
		return bitmap

	def print_data(self, f, mode = "values"):
		assert(mode in [ "values", "dots" ])
		dot = "⬤ "
		charspace = {
			"values":	" ",
			"dots":		"",
		}[mode]
		for y in range(self.height):
			line = [ ]
			for x in range(self.width):
				if mode == "values":
					value = "%3d" % (self.get_pixel(x, y))
				elif mode == "dots":
					value = dot if (self.get_pixel(x, y) == 0) else "  "
				else:
					raise NotImplementedError(mode)
				line.append(value)
			print(charspace.join(line), file = f)

	def serialize(self):
		return {
			"codepoint":	self.codepoint,
			"width":		self.width,
			"height":		self.height,
			"xoffset":		self.xoffset,
			"yoffset":		self.yoffset,
			"xadvance":		self.xadvance,
			"data":			self._raw_data.hex(),
		}

	@classmethod
	def deserialize(cls, glyph_data):
		return cls(codepoint = glyph_data["codepoint"], width = glyph_data["width"], height = glyph_data["height"], xoffset = glyph_data["xoffset"], yoffset = glyph_data["yoffset"], xadvance = glyph_data.get("xadvance", 0), raw_data = bytes.fromhex(glyph_data["data"]))

	def __str__(self):
		return "Glyph<\"%s\", %d x %d, %d bytes>" % (self.codepoint, self.width, self.height, len(self.raw_data))
