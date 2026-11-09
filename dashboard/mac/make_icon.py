"""Make a 1024x1024 app-icon PNG from any square image: the image is scaled to 824 px and centred
on a transparent canvas (the standard macOS icon margin). Reads the source only.
Run with the venv python (needs AppKit from pyobjc):  python make_icon.py SOURCE.png OUT.png
"""
import sys
from AppKit import (NSBitmapImageRep, NSCalibratedRGBColorSpace, NSCompositingOperationSourceOver,
                    NSGraphicsContext, NSImage, NSImageInterpolationHigh, NSMakeRect, NSPNGFileType, NSZeroRect)

SIZE, ART = 1024, 824

src, out = sys.argv[1], sys.argv[2]
img = NSImage.alloc().initWithContentsOfFile_(src)
if img is None:
    sys.exit('Cannot read ' + src)
rep = NSBitmapImageRep.alloc().initWithBitmapDataPlanes_pixelsWide_pixelsHigh_bitsPerSample_samplesPerPixel_hasAlpha_isPlanar_colorSpaceName_bytesPerRow_bitsPerPixel_(
    None, SIZE, SIZE, 8, 4, True, False, NSCalibratedRGBColorSpace, 0, 0)
ctx = NSGraphicsContext.graphicsContextWithBitmapImageRep_(rep)
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.setCurrentContext_(ctx)
ctx.setImageInterpolation_(NSImageInterpolationHigh)
m = (SIZE - ART) / 2
img.drawInRect_fromRect_operation_fraction_(NSMakeRect(m, m, ART, ART), NSZeroRect, NSCompositingOperationSourceOver, 1.0)
NSGraphicsContext.restoreGraphicsState()
rep.representationUsingType_properties_(NSPNGFileType, {}).writeToFile_atomically_(out, True)
