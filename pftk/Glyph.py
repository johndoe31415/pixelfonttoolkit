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

class BitmapGlyph(object):
	def __init__(self, data, glyph):
		assert(len(data) == glyph.width * glyph.height)
		self._bitmap_data = [ ]
		self._glyph = glyph

		for y in range(self._glyph.height):
			for x0 in range(0, self._glyph.width, 8):
				databyte = 0
				for xoffset in range(8):
					x = x0 + xoffset
					if x >= self._glyph.width:
						bitvalue = 0
					else:
						bitvalue = int(data[x + (y * self._glyph.width)])
					databyte = (databyte >> 1) | (0x80 * bitvalue)
				self._bitmap_data.append(databyte)

	@property
	def glyph(self):
		return self._glyph

	@property
	def data(self):
		return bytes(self._bitmap_data)

	@property
	def row_width(self):
		return (self._glyph.width + 7) // 8

	def get_pixel(self, x, y):
		byte_offset = (x // 8) + (y * self.row_width)
		bit_offset = x % 8
		return ((self._bitmap_data[byte_offset] >> bit_offset) & 1) != 0

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

	def blit_to(self, pic, x0, y0, auto_offset = True):
		for gy in range(self._glyph.height):
			for gx in range(self._glyph.width):
				if self.get_pixel(gx, gy):
					x = x0 + gx
					y = y0 + gy
					if auto_offset:
						x += self._glyph.xoffset
						y += self._glyph.yoffset
					pic.set_pixel(x, y, (0, 0, 0))

class Glyph(object):
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
		return self._raw_data[(y * self.width) + x]

	def iter_set_pixels(self, threshold = 128, mode = "real", ref = (0, 0)):
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
