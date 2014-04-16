

from copy import copy

from PyQt5.QtCore import QSize, QSizeF
from PyQt5.QtPrintSupport import QPrinter


class OrientedSize(object):
  '''
  General methods for dealing with orientation,
  oriented sizes, and conversions.
  '''
  
  @classmethod
  def roundedSize(cls, sizeF):
    '''
    Rounded size, or None (when sizeF is huge, meaning: unknown)
    Undocumented Qt behaviour: returns huge paperSize for unknown.
    '''
    assert isinstance(sizeF, QSizeF)
    integralWidth = int(round(sizeF.width()))
    integralHeight = int(round(sizeF.height()))
    
    '''
    May be Python type 'long', which QSize will not accept.
    '''
    try:
      result = QSize(integralWidth, integralHeight )
    except TypeError:
      result = None  # ugly premature return
    return result
  
  @classmethod
  def normalizedSize(cls, size):
    '''
    Normalized means: QSize having width <= height
    # TODO copy
    # TODO use transpose
    '''
    assert isinstance(size, QSize) # Algorithm would work for QSizeF
    if size.width() > size.height():
      result = size.transposed()
    else:
      result = copy(size)
    assert isinstance(result, QSize)
    assert not result is size
    return result
  
  
  @classmethod
  def portraitSizeMM(cls, size, orientation):
    '''
    Portrait only means: one of two orientations.
    Custom paper can be defined in portrait orientation, but not normalized.
    
    size may be QSize or QSizeF, and result is same type
    Returns a copy.
    '''
    # i.e. an alias
    return cls.orientedSize(size, orientation)
  
  
  @classmethod
  def orientedSize(cls, size, orientation):
    '''
    size may be QSize or QSizeF, and result is same type
    Returns a copy.
    '''
    if orientation == QPrinter.Portrait:
      result = copy(size)
    else:
      result = size.transposed() # QSize method, copy with swapped width and height
    assert not result is size
    # it is NOT an assertion that result is normalized
    return result
  
  
  @classmethod
  def orientationName(cls, orientation):
      if orientation == 0:
          return 'Portrait'
      else:
          return 'Landscape'

