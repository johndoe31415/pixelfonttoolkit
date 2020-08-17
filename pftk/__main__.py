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
from .MultiCommand import MultiCommand
from .ActionImportImage import ActionImportImage
from .ActionConvert import ActionConvert
from .ActionDraw import ActionDraw
from .ActionManipulate import ActionManipulate

mc = MultiCommand()

def genparser(parser):
	parser.add_argument("-g", "--glyphs", metavar = "glyphstr", required = True, help = "Specifies the characters that correspond to the imported glyphs. Mandatory argument.")
	parser.add_argument("-o", "--outfile", metavar = "filename", required = True, help = "Specifies the output file which should be written. Mandatory argument.")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times to increase even more.")
	parser.add_argument("png_image", help = "PNG image to import")
mc.register("import", "Import a pixel image into the PFG native format", genparser, action = ActionImportImage)

def genparser(parser):
	parser.add_argument("-f", "--format", choices = [ "ascii", "bitfontmaker" ], default = "ascii", help = "Specifies the output format to write. Can be one of %(choices)s, defaults to %(default)s.")
	parser.add_argument("-o", "--outfile", metavar = "filename", required = True, help = "Specifies the output file which should be written. Mandatory argument.")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times to increase even more.")
	parser.add_argument("font_filename", help = "Font filename to read")
mc.register("convert", "Convert a pftk native font into something else", genparser, action = ActionConvert)

def genparser(parser):
	parser.add_argument("-t", "--text", metavar = "text", default = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", help = "Text to draw. Defaults to '%(default)s'.")
	parser.add_argument("-o", "--outfile", metavar = "filename", required = True, help = "Specifies the output file which should be written. Mandatory argument.")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times to increase even more.")
	parser.add_argument("font_filename", help = "Font filename to read")
mc.register("draw", "Draw some text using a font into a PNG image", genparser, action = ActionDraw)

def genparser(parser):
	parser.add_argument("-g", "--glyphs", metavar = "glyphstr", help = "Specifies which glyphs to apply manipulator to. By default applies to all glyphs.")
	parser.add_argument("-i", "--infile", metavar = "filename", required = True, help = "Specifies the input font file which should be read. Mandatory argument.")
	parser.add_argument("-o", "--outfile", metavar = "filename", required = True, help = "Specifies the output font file which should be written. Mandatory argument.")
	parser.add_argument("-v", "--verbose", action = "count", default = 0, help = "Increase verbosity. Can be specified multiple times to increase even more.")
	parser.add_argument("manipulator", type = ActionManipulate.parse_manipulator, nargs = "+", help = "Manipulator to apply to glyph(s)")
mc.register("manipulate", "Manipulate a font", genparser, action = ActionManipulate)

mc.run(sys.argv[1:])
