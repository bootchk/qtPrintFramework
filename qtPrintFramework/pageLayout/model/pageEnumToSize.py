
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

'''
  Dictionary from enum to integral QSize in mm.
  
  This IS a binary relation.
  In other words, no two papers (having different names) have the same size.
  
  The sizes are 'defined size' which are defined in Portrait orientation.
  Not assert every QSize is normalized, i.e. has width < height.
  Two defined sizes are not the same even if they are the same form factor(pair of number in different order.)
  See Ledger and Tabloid, which have the same form factor (occupies the same space after rotating one) but not same size.
  
  Assert this includes every value from QPagedPaintDevice.PageSize enumerated type, EXCEPT for Custom.
  
  Derived from QPagedPaintDevice.PageSize
'''

pageEnumToSize = { 
    QPagedPaintDevice.A0 : QSize(841, 1189),
    QPagedPaintDevice.A1  : QSize(594, 841),
    QPagedPaintDevice.A2  : QSize(420, 594),
    QPagedPaintDevice.A3  : QSize(297, 420),
    QPagedPaintDevice.A4  : QSize(210, 297),
    QPagedPaintDevice.A5  : QSize(148, 210),
    QPagedPaintDevice.A6  : QSize(105, 148),
    QPagedPaintDevice.A7  : QSize(74, 105),
    QPagedPaintDevice.A8  : QSize(52, 74),
    QPagedPaintDevice.A9  : QSize(37, 52),
    QPagedPaintDevice.B0  : QSize(1000, 1414),
    QPagedPaintDevice.B1  : QSize(707, 1000),
    QPagedPaintDevice.B2  : QSize(500, 707),
    QPagedPaintDevice.B3  : QSize(353, 500),
    QPagedPaintDevice.B4  : QSize(250, 353),
    QPagedPaintDevice.B5  : QSize(176, 250),
    QPagedPaintDevice.B6  : QSize(125, 176),
    QPagedPaintDevice.B7  : QSize(88, 125),
    QPagedPaintDevice.B8  : QSize(62, 88),
    QPagedPaintDevice.B9  : QSize(44, 62),
    QPagedPaintDevice.B10  : QSize(31, 44), 
    QPagedPaintDevice.C5E  : QSize(163, 229),
    QPagedPaintDevice.Comm10E  : QSize(105, 241),
    QPagedPaintDevice.DLE  : QSize(110, 220),
    # Following entries are hacked from Qt docs: rounded from fractional mm, or otherwise altered
    # Comments tell whether they meet ANSI Standard, or are loose standards.
    QPagedPaintDevice.Executive  : QSize(191, 254), # ? Wiki says (184, 267)
    QPagedPaintDevice.Folio  : QSize(210, 330),     # Loose
    QPagedPaintDevice.Ledger  : QSize(432, 279),    # Same form as Tabloid.
    QPagedPaintDevice.Legal  : QSize(216, 356),     # Loose
    QPagedPaintDevice.Letter  : QSize(216, 279),    # ANSI
    QPagedPaintDevice.Tabloid  : QSize(279, 432),   # ANSI
    # QPagedPaintDevice.Custom  30  Unknown, or a user defined size.
    }


'''
Inverse of above, except convert QSize to hashable tuple
'''
pageSizeToEnum = {(v.width(), v.height()):k for k, v in pageEnumToSize.items()}

assert len(pageSizeToEnum) == len(pageEnumToSize), "Binary relation"

