'''
'''
from PyQt5.QtCore import QSize, QSizeF
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

from qtPrintFramework.model.adaptedModel import AdaptedModel

class Paper(object):
  '''
  Wrapper around QPagedPaintDevice.PageSize
  
  ABC
  Inherited by:
  - StandardPaper: has size
  - CustomPaper: has no size
  Future: NonStandardPaper: defined by a printer, having a size and name.
  
  !!! a Paper does not know its orientation.
  '''
  nameModel = AdaptedModel._getAdaptedReverseDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion
  
  '''
  Dictionary from enum to integral QSize in mm.
  
  This is NOT a binary relation, see Ledger and Tabloid
  In other words, two papers having different names have the same dimensions (if oriented narrow dimension vertical.)
  
  Assert this includes every value from QPagedPaintDevice.PageSize enumerated type.
  Assert every QSize has width < height (which differs from Qt.)
  Wrapper around QPagedPaintDevice.PageSize
  '''
  sizeModel = { 
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
    QPagedPaintDevice.Ledger  : QSize(279, 432),    # Same as Tabloid. But differs from Qt reversed width and height
    QPagedPaintDevice.Legal  : QSize(216, 356),     # Loose
    QPagedPaintDevice.Letter  : QSize(216, 279),    # ANSI
    QPagedPaintDevice.Tabloid  : QSize(279, 432),   # ANSI
    # QPagedPaintDevice.Custom  30  Unknown, or a user defined size.
    }
  
  # Convert QSize to hashable tuple.
  # TODO, but it is not a binary relation !!!
  inverseSizeModel = {(v.width(), v.height()):k for k, v in sizeModel.items()}
  #print(Paper.inverseSizeModel)
    
    
  @classmethod
  def enumForPageSizeByMatchDimensions(cls, paperSizeMM):
    '''
    Returns enum from type QPagedPaintDevice.PageSize using fuzzy match on paper dimensions.
    
    The fuzziness is: 0.5 mm
    That is, we round mm fractional sizes to int.
    This is the kind of floating point inaccuracy that the Qt bug introduces: off by less than 0.5.
    
    !!! But note that Qt returns paperSizeMM that reflects orientation, i.e. width can be > height
    '''
    assert isinstance(paperSizeMM, QSizeF)
    integralWidth = int(round(paperSizeMM.width()))
    integralHeight = int(round(paperSizeMM.height()))
    
    '''
    May be Python type 'long', which QSize will not accept.
    '''
    try:
      roundedSize = QSize(integralWidth, integralHeight )
    except TypeError:
      return None  # ugly premature return
    
    normalizedRoundedSize = cls._normalizedPaperSize(roundedSize)
    hashedNormalizedRoundedSize = (normalizedRoundedSize.width(), normalizedRoundedSize.height())
    #print(hashedNormalizedRoundedSize)
    try:
      result = cls.inverseSizeModel[hashedNormalizedRoundedSize]
    except KeyError:
      print("KeyError in enumForPageSizeByMatchDimensions:", paperSizeMM.width(), ',', paperSizeMM.height())
      result = None
    return result
  
  @classmethod
  def _normalizedPaperSize(cls, paperSize):
    '''
    Normalized means: QSize having width <= height
    '''
    assert isinstance(paperSize, QSize) # Algorithm would work for QSizeF
    if paperSize.width() > paperSize.height():
      result = QSize(paperSize.height(), paperSize.width())
    else:
      result = paperSize
    assert isinstance(result, QSize)
    return result
  
    
  def __init__(self, paperEnum):
    '''
    Default: CustomPaper overrides: still has this attribute but is constant
    '''
    # this is the best assertion we can do?  Fragile?
    assert paperEnum is not None
    assert isinstance(paperEnum, int), str(type(paperEnum))
    #assert str(type(paperEnum)) == "<type 'sip.enumtype'>"
    #assert isinstance(paperEnum, QPagedPaintDevice.PageSize)
    
    self.paperEnum = paperEnum
  
  
  def __repr__(self):
    raise NotImplementedError, 'Deferred'
  
  
  def __eq__(self, other):
    '''
    Two instances are equal if they have the same value from enum QPagedPaintDevice.PageSize.
    An instance of Paper represents a user choice.  There may be many instances.
    Without implementing this, == returns False for separate instances.
    '''
    return self.paperEnum == other.paperEnum
  
  
  @property
  def name(self):
    raise NotImplementedError, 'Deferred'
  

  @property
  def isStandard(self):
    '''
    Compare with isCustom().
    Is standardized by some organization?
    Loosely, name is well-known and means the same thing around the world.
    See above, some really are not rigorously standardized, only loosely standardize.
    
    Deferred: subclasses must reimplement.
    '''
    raise NotImplementedError, 'Deferred'
    
  @property
  def isCustom(self):
    return not self.isStandard
  
  
  
