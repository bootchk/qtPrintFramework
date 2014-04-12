'''
'''

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import QSize, QSizeF

from qtPrintFramework.paper.paper import Paper


class StandardPaper(Paper):
  '''
  Paper of a limited set:
  - standardized by a standards organization (sic)
  - supported across platform by Qt
  '''
  
  def __repr__(self):
    ''' Human readable description including name and dimensions in mm. '''
    size = self.integralSizeMM
    return self.name + " " + str(size.width()) + 'x' + str(size.height()) + 'mm'
  
  
  @property
  def name(self):
    '''
    Implement deferred.
    '''
    return  Paper.nameModel[self.paperEnum]
  
  
  '''
  paperEnum attribute inherited
  '''
  
  '''
  Only StandardPaper has size.
  '''
  
  def orientedSizeMM(self, orientation):
    '''
    QSize oriented.  Integer
    '''
    if orientation == QPrinter.Portrait:
      result = self.integralSizeMM
    else:
      result = self.integralSizeMM.transposed() # QSize method, swap width and height
    assert isinstance(result, QSize)
    # Oriented does not imply normalized
    # assert result.width() > result.height() or result.width() <= result.height()
    return result
  
  @property
  def integralSizeMM(self):
    '''
    Default: subclasses may override.
    '''
    result = Paper.sizeModel[self.paperEnum]
    assert isinstance(result, QSize)
    return result
  
  
  def isOrientedSizeEpsilonEqual(self, orientation, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    
    integralOrientedSize = self.orientedSizeMM(orientation)
    result = abs(integralOrientedSize.width() - sizeF.width()) < 0.5 \
            and abs(integralOrientedSize.height() - sizeF.height()) < 0.5
    return result
  
  def isSizeEpsilonEqual(self, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    
    integralSize = self.integralSizeMM
    result = abs(integralSize.width() - sizeF.width()) < 0.5 \
            and abs(integralSize.height() - sizeF.height()) < 0.5
    return result
    
    
  @property
  def isStandard(self):
    '''
    Implement deferred
    '''
    return True

  
  
  
