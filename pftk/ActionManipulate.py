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

import enum
import argparse
import collections
from .BaseAction import BaseAction
from .Font import Font
from .Glyph import Glyph

class Manipulator(enum.Enum):
	Optimize = "optimize"
	ShiftRight = "shift_right"
	ShiftLeft = "shift_left"
	ShiftUp = "shift_up"
	ShiftDown = "shift_down"
	ShiftX = "shift_x"
	ShiftY = "shift_y"
	Monospace = "monospace"

class ActionManipulate(BaseAction):
	_Manipulator = collections.namedtuple("Manipulator", [ "action", "args" ])
	_ArgumentCount = {
		Manipulator.Optimize:	0,
	}

	@classmethod
	def parse_manipulator(cls, man_text):
		man = man_text.split(",")
		try:
			action = Manipulator(man[0])
			args = man[1:]
		except ValueError:
			raise argparse.ArgumentTypeError("Invalid manipulator given: %s (must be one of %s)" % (man[0], ", ".join(sorted(manipulator.value for manipulator in Manipulator))))
		argument_count = cls._ArgumentCount.get(action, 1)
		if len(args) != argument_count:
			raise argparse.ArgumentTypeError("Invalid manipulator argument count: %s requires %d argument(s), but %d given." % (action.name, argument_count, len(man) - 1))

		if action == Manipulator.ShiftRight:
			(action, args) = (Manipulator.ShiftX, [ int(args[0]) ])
		elif action == Manipulator.ShiftLeft:
			(action, args) = (Manipulator.ShiftX, [ -int(args[0]) ])
		elif action == Manipulator.ShiftUp:
			(action, args) = (Manipulator.ShiftY, [ -int(args[0]) ])
		elif action == Manipulator.ShiftDown:
			(action, args) = (Manipulator.ShiftY, [ int(args[0]) ])
		elif action in [ Manipulator.ShiftX, Manipulator.ShiftY, Manipulator.Monospace ]:
			args = [ int(args[0]) ]
		return cls._Manipulator(action = action, args = args)

	def _manipulate_ShiftX(self, glyph, shift):
		return Glyph(codepoint = glyph.codepoint, width = glyph.width, height = glyph.height, xoffset = glyph.xoffset + shift, yoffset = glyph.yoffset, xadvance = glyph.xadvance, raw_data = glyph.raw_data)

	def _manipulate_ShiftY(self, glyph, shift):
		return Glyph(codepoint = glyph.codepoint, width = glyph.width, height = glyph.height, xoffset = glyph.xoffset, yoffset = glyph.yoffset + shift, xadvance = glyph.xadvance, raw_data = glyph.raw_data)

	def _manipulate_Monospace(self, glyph, xadvance):
		return Glyph(codepoint = glyph.codepoint, width = glyph.width, height = glyph.height, xoffset = glyph.xoffset, yoffset = glyph.yoffset, xadvance = xadvance, raw_data = glyph.raw_data)

	def _manipulate_Optimize(self, glyph):
		return glyph.optimize()

	def _manipulate(self, glyph, manipulator):
		method_name = "_manipulate_" + manipulator.action.name
		method = getattr(self, method_name)
		return method(glyph, *manipulator.args)

	def run(self):
		self._font = Font.load_from_file(self._args.infile)
		if self._args.glyphs is None:
			glyphs = self._font.get_all_glyphs()
		else:
			glyphs = [ self._font.get_glyph(codepoint) for codepoint in set(self._args.glyphs) ]
		glyphs = [ glyph for glyph in glyphs if glyph is not None ]
		for manipulator in self._args.manipulator:
			glyphs = [ self._manipulate(glyph, manipulator) for glyph in glyphs ]
		for glyph in glyphs:
			self._font.replace_glyph(glyph)
		self._font.save_to_file(self._args.outfile)
