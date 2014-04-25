

from copy import copy

from PyQt5.QtCore import QObject, QSize, QSizeF



class OrientedSize(QObject):
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
    '''
    assert isinstance(size, QSize) # Algorithm would work for QSizeF
    if size.width() > size.height():
      result = size.transposed()  
    else:
      result = copy(size)
    assert isinstance(result, QSize)
    assert not result is size,  'returns a new object'
    return result
  
  
  @classmethod
  def portraitSizeMM(cls, size, orientation):
    '''
    Portrait only means: one of two orientations.
    Custom paper can be defined in portrait orientation, but not normalized.
    
    size may be QSize or QSizeF, and result is same type
    Returns a copy.
    
    Since definitions are portrait, this could also be called 'definedSizeMM.'
    '''
    # i.e. an alias
    return cls.orientedSize(size, orientation)
  
  
  @classmethod
  def orientedSize(cls, size, orientation):
    '''
    size may be QSize or QSizeF, and result is same type
    Returns a copy.
    '''
    if orientation.isPortrait:
      result = copy(size)
    else:
      result = size.transposed() # QSize method, copy with swapped width and height
    assert not result is size
    # it is NOT an assertion that result is normalized
    return result


  @classmethod
  def areSizesEpsilonEqual(cls, size1, size2):
    '''
    Are two sizes equal to within a small epsilon.
    i.e. deal with floating point imprecision.
    '''
    result = abs(size1.width() - size2.width()) < 0.5 \
            and abs(size1.height() - size2.height()) < 0.5
    return result
  
  