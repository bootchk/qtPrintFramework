
from PyQt5.QtCore import QObject, QSize, QSizeF, pyqtSignal, pyqtProperty


from qtPrintFramework.pageLayout.model.pageNameToEnum import pageEnumToName
from qtPrintFramework.pageLayout.model.pageEnumToSize import pageEnumToSize, pageSizeToEnum

from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.alertLog import alertLog



class Paper(QObject):
  '''
  Page??
  
  ABC
  Inherited by:
  - StandardPaper: size defined by a standard model
  - CustomPaper: size defined by user (or a default)
  Future: NonStandardPaper: defined by a printer
  
  Responsibilities:
  - name
  - enum, constant that Qt uses: QPagedPaintDevice.PageSize or QPageLayout.PageSize ??
  - orientedDescription
  - knows whether it is Custom
  - size in various flavors
  -- integralOrientedSizeMM
  - equality
  - how to derive enum from a floating size from Qt: enumForPageSizeByMatchDimensions
  
  !!! a Paper does not know its orientation (it is passed) but knows it's oriented description.
  '''
  
  valueChanged = pyqtSignal(int)
  
  " Dictionaries used as models. "
  nameModel = pageEnumToName
  sizeModel = pageEnumToSize
  inverseSizeModel = pageSizeToEnum
    
    
  @classmethod
  def enumForPageSizeByMatchDimensions(cls, paperSizeMM, orientationEnum):
    '''
    Returns enum from type QPagedPaintDevice.PageSize using fuzzy match on paper dimensions.
    
    The fuzziness is: 0.5 mm
    That is, we round mm fractional sizes to int.
    This is the kind of floating point inaccuracy that the Qt bug introduces: off by less than 0.5.
    
    !!! But note that Qt returns paperSizeMM that reflects orientation, i.e. width can be > height
    '''
    assert isinstance(orientationEnum, int)
    roundedSize = OrientedSize.roundedSize(sizeF=paperSizeMM)
    if roundedSize is None:
      return None
    
    definedRoundedSize = OrientedSize.portraitSizeMM(roundedSize, orientationEnum)
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
    super().__init__()  # init QObject
    
    # this is the best assertion we can do?  Fragile?
    if initialValue is not None:
      assert isinstance(initialValue, int), str(type(initialValue))
      #assert str(type(value)) == "<type 'sip.enumtype'>"
      #assert isinstance(value, QPagedPaintDevice.PageSize)
      
      self._value = initialValue
    else:
      self._value = 0  # QPagedPaintDevice.A0 ?
  
  
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
      result = self._value == other._value
    else:
      result = self._value == other._value \
              and self.hasEqualSizeTo(other)
    return result


  '''
  Crux data is an enum, a Qt property with notifiable signal.
  '''
  @pyqtProperty(int, notify=valueChanged)
  def value(self):
    return self._value
  
  @value.setter
  def value(self, newValue):
    self._value = newValue
    self.valueChanged.emit(newValue)
  
  
  
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
  
  
  '''
  Deferred property
  def name(self):
    raise NotImplementedError('Deferred')
  '''
  

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
  
  inverseSizeModel
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
  
