'''
'''
from PyQt5.QtCore import QSize, QSizeF
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.model.adaptedModel import AdaptedModel

class Paper(object):
  '''
  Wrapper around QPagedPaintDevice.PageSize
  '''
  nameModel = AdaptedModel._getAdaptedReverseDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion
  
  '''
  Dictionary from enum to integral QSize in mm.
  
  This is NOT a binary relation, see Ledger and Tabloid
  In other words, two papers having different names have the same dimensions (if oriented narrow dimension vertical.)
  
  Assert this includes every value from QPagedPaintDevice.PageSize enumerated type.
  Assert every QSize has width < height (which differs from Qt.)
  
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
    QPagedPaintDevice.Executive  : QSize(184, 267), # Different from Qt ~ 191, 254?
    QPagedPaintDevice.Folio  : QSize(210, 330),   # Loose
    QPagedPaintDevice.Ledger  : QSize(279, 432),  # Same as Tabloid. But differs from Qt reversed width and height
    QPagedPaintDevice.Legal  : QSize(216, 356),   # Loose
    QPagedPaintDevice.Letter  : QSize(216, 279),  # ANSI
    QPagedPaintDevice.Tabloid  : QSize(279, 432), # ANSI
    # QPagedPaintDevice.Custom  30  Unknown, or a user defined size.
    }
  
  # Convert QSize to hashable tuple.
  # TODO, but it is not a binary relation !!!
  inverseSizeModel = {(v.width(), v.height()):k for k, v in sizeModel.items()}
  #print(Paper.inverseSizeModel)
    
    
  @classmethod
  def fuzzyMatchPageSize(cls, paperSizeMM):
    '''
    Returns enum from type QPagedPaintDevice.PageSize using fuzzy match.
    
    The fuzziness is: 0.5 mm
    That is, we round mm fractional sizes to int.
    This is the kind of floating point inaccuracy that the Qt bug introduces: off by less than 0.5.
    
    !!! But note that Qt returns paperSizeMM that reflects orientation, i.e. width can be > height
    '''
    assert isinstance(paperSizeMM, QSizeF)
    roundedSize = QSize(int(round(paperSizeMM.width())), 
                        int(round(paperSizeMM.height()))
                        )
    
    normalizedRoundedSize = cls._normalizedPaperSize(roundedSize)
    hashedNormalizedRoundedSize = (normalizedRoundedSize.width(), normalizedRoundedSize.height())
    #print(hashedNormalizedRoundedSize)
    try:
      result = cls.inverseSizeModel[hashedNormalizedRoundedSize]
    except KeyError:
      print("KeyError")
      result = None
    return result
  
  @classmethod
  def _normalizedPaperSize(cls, paperSize):
    '''
    QSize having width <= height
    '''
    assert isinstance(paperSize, QSize) # Algorithm would work for QSizeF
    if paperSize.width() > paperSize.height():
      result = QSize(paperSize.height(), paperSize.width())
    else:
      result = paperSize
    assert isinstance(result, QSize)
    return result
  
    
  def __init__(self, pageSize):
    #assert isinstance(pageSize, enumtype)
    assert pageSize is not None
    self.pageSize = pageSize
  
  
  def __repr__(self):
    ''' Human readable description including name and dimensions in mm. '''
    size = self.integralSizeMM
    return self.name + " " + str(size.width()) + 'x' + str(size.height()) + 'mm'
  
  def __eq__(self, other):
    '''
    Two instances are equal if they have the same value from enum QPagedPaintDevice.PageSize.
    An instance of Paper represents a user choice.  There may be many instances.
    Without implementing this, == returns False for separate instances.
    '''
    return self.pageSize == other.pageSize
  
  
  @property
  def name(self):
    return  Paper.nameModel[self.pageSize]
  
  @property
  def paperSize(self):
    " Enum value "
    return self.pageSize  # sic, thats the name Qt uses
  
  
  def orientedSizeMM(self, orientation):
    '''
    QSize oriented
    '''
    if orientation == QPrinter.Portrait:
      result = self.integralSizeMM
    else:
      result = Paper.rotatedPaperSize(self.integralSizeMM)
    assert isinstance(result, QSize)
    return result
  
  @property
  def integralSizeMM(self):
    '''
    Default: subclasses may override.
    '''
    result = Paper.sizeModel[self.pageSize]
    assert isinstance(result, QSize)
    return result
  
    
  def isStandard(self):
    '''
    Compare with isCustom().
    Is standardized by some organization?
    Loosely, name is well-known and means the same thing around the world.
    See above, some really are not rigorously standardized, only loosely standardize.
    
    Default:subclasses may reimplement.
    '''
    return True
    
  def isCustom(self):
    return not self.isStandard()
  
  
  
