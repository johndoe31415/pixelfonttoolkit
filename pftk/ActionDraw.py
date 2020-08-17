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

from .BaseAction import BaseAction
from .Font import Font
import PIL.Image, PIL.ImageDraw

class ActionDraw(BaseAction):
	def _start_draw(self, x, y):
		self._img.putpixel((x, y), (255, 0, 0, 100))

	def _put_pixel(self, x, y):
		self._img.putpixel((x, y), (0, 0, 0, 200))

	def _end_draw(self, x, y):
		self._img.putpixel((x, y), (0, 255, 0, 100))

	def run(self):
		self._font = Font.load_from_file(self._args.font_filename)
		self._extents = self._font.get_text_extents(self._args.text)

		self._img = PIL.Image.new("RGBA", (self._extents.width + 20, self._extents.height + 20))
		self._draw = PIL.ImageDraw.Draw(self._img)
		self._font.write(self._args.text, 10, self._img.height - 10 - self._extents.height_below_baseline, callback_put_pixel = self._put_pixel, callback_start_draw = self._start_draw, callback_end_draw = self._end_draw)
		self._img.save(self._args.outfile)
