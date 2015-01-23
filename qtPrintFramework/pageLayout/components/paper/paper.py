
from PyQt5.QtCore import QSize, QSizeF
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport


from qtPrintFramework.pageLayout.model.adaptedModel import AdaptedModel
from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.alertLog import alertLog

class Paper(object):
  '''
  Wrapper around QPagedPaintDevice.PageSize
  
  ABC
  Inherited by:
  - StandardPaper: size defined by a standard model
  - CustomPaper: size defined by user (or a default)
  Future: NonStandardPaper: defined by a printer
  
  Responsibilities:
  - name
  - enum, constant that Qt uses
  - orientedDescription
  - knows whether it is Custom
  - size in various flavors
  -- integralOrientedSizeMM
  - equality
  - how to derive enum from a floating size from Qt: enumForPageSizeByMatchDimensions
  
  !!! a Paper does not know its orientation (it is passed) but knows it's oriented description.
  '''
  nameModel = AdaptedModel._getAdaptedReverseDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion
  
  '''
  Dictionary from enum to integral QSize in mm.
  
  This IS a binary relation.
  In other words, no two papers (having different names) have the same size.
  
  The sizes are 'defined size' which are defined in Portrait orientation.
  Not assert every QSize is normalized, i.e. has width < height.
  Two defined sizes are not the same even if they are the same form factor(pair of number in different order.)
  See Ledger and Tabloid, which have the same form factor (occupies the same space after rotating one) but not same size.
  
  Assert this includes every value from QPagedPaintDevice.PageSize enumerated type, EXCEPT for Custom.
  
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
    QPagedPaintDevice.Ledger  : QSize(432, 279),    # Same form as Tabloid.
    QPagedPaintDevice.Legal  : QSize(216, 356),     # Loose
    QPagedPaintDevice.Letter  : QSize(216, 279),    # ANSI
    QPagedPaintDevice.Tabloid  : QSize(279, 432),   # ANSI
    # QPagedPaintDevice.Custom  30  Unknown, or a user defined size.
    }
  
  '''
  Inverse dictionary
  
  Part of process is convert QSize to hashable tuple.
  '''
  inverseSizeModel = {(v.width(), v.height()):k for k, v in sizeModel.items()}
  assert len(inverseSizeModel) == len(sizeModel), "Binary relation"
  #print(Paper.inverseSizeModel)
    
    
  @classmethod
  def enumForPageSizeByMatchDimensions(cls, paperSizeMM, orientation):
    '''
    Returns enum from type QPagedPaintDevice.PageSize using fuzzy match on paper dimensions.
    
    The fuzziness is: 0.5 mm
    That is, we round mm fractional sizes to int.
    This is the kind of floating point inaccuracy that the Qt bug introduces: off by less than 0.5.
    
    !!! But note that Qt returns paperSizeMM that reflects orientation, i.e. width can be > height
    '''
    roundedSize = OrientedSize.roundedSize(sizeF=paperSizeMM)
    if roundedSize is None:
      return None
    
    definedRoundedSize = OrientedSize.portraitSizeMM(roundedSize, orientation)
    hashedDefinedRoundedSize = (definedRoundedSize.width(), definedRoundedSize.height())
    #print(hashedDefinedRoundedSize)
    try:
      result = cls.inverseSizeModel[hashedDefinedRoundedSize]
    except KeyError:
      alertLog("KeyError in enumForPageSizeByMatchDimensions: {} {}".format(paperSizeMM.width(),paperSizeMM.height()))
      result = None
    return result
    
   
  
  def __init__(self, initialValue):
    '''
    Default: CustomPaper overrides: still has this attribute but is constant
    '''
    # this is the best assertion we can do?  Fragile?
    if initialValue is not None:
      assert isinstance(initialValue, int), str(type(initialValue))
      #assert str(type(paperEnum)) == "<type 'sip.enumtype'>"
      #assert isinstance(paperEnum, QPagedPaintDevice.PageSize)
      
      self.paperEnum = initialValue
    else:
      self.paperEnum = 0  # QPagedPaintDevice.A0 ?
  
  
  def __repr__(self):
    ''' 
    Human readable description including name, dimensions in mm.
    
    # !!! Not oriented.  A paper does not know its orientation.
    '''
    return "Unoriented " + self.name + " " + self._definedSizeString  
  
  
  def __eq__(self, other):
    '''
    Two instances are equal if they have the same value from enum QPagedPaintDevice.PageSize
    AND if they are both custom, they also have equal portrait sizes.
    
    An instance of Paper represents a user choice.  There may be many instances.
    Without implementing this, == returns False for separate instances.
    
    !!! This compares portrait size.
    Usually caller already knows the orientation is equal.
    Used to determine whether pageSetup has changed.
    '''
    if not self.isCustom:
      result = self.paperEnum == other.paperEnum
    else:
      result = self.paperEnum == other.paperEnum \
              and self.hasEqualSizeTo(other)
    return result

  
  @property
  def _definedSizeString(self):
    " string for defined size  (not oriented.) "
    size = self.integralDefinedSizeMM
    return str(size.width()) + 'x' + str(size.height()) + 'mm'
  
  def orientedDescription(self, orientation):
    ''' Human readable description also oriented. '''
    return " ".join(( self.name, orientation.name, self._orientedSizeString(orientation)))
  
  def _orientedSizeString(self, orientation):
    " string for oriented size  "
    size = self.integralOrientedSizeMM(orientation)
    return str(size.width()) + 'x' + str(size.height()) + 'mm'
  
  
  @property
  def name(self):
    raise NotImplementedError('Deferred')
  

  @property
  def isStandard(self):
    '''
    Compare with isCustom().
    Is standardized by some organization?
    Loosely, name is well-known and means the same thing around the world.
    See above, some really are not rigorously standardized, only loosely standardize.
    
    Deferred: subclasses must reimplement.
    '''
    raise NotImplementedError('Deferred')
    
  @property
  def isCustom(self):
    return not self.isStandard
  
  
  def integralOrientedSizeMM(self, orientation):
    '''
    QSize oriented.  Integer. Units mm
    '''
    # integralDefinedSizeMM is property of subclass
    result = OrientedSize.orientedSize(self.integralDefinedSizeMM, orientation)
    assert isinstance(result, QSize)
    # Oriented does not imply normalized
    # assert result.width() > result.height() or result.width() <= result.height()
    return result
  
  
  
  '''
  Tests for epsilon equality.
  
  Oriented and Defined are two opposing choices:
  Caller must insure the passed size has the same property, oriented or defined.
  '''
  
  def isOrientedSizeEpsilonEqual(self, orientation, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    integralOrientedSize = self.integralOrientedSizeMM(orientation)
    result = OrientedSize.areSizesEpsilonEqual(integralOrientedSize, sizeF)
    return result
  
  
  def isDefinedSizeEpsilonEqual(self, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    integralSize = self.integralDefinedSizeMM
    result = OrientedSize.areSizesEpsilonEqual(integralSize, sizeF)
    return result
  
