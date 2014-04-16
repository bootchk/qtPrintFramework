

from PyQt5.QtCore import QSize, QSizeF

from qtPrintFramework.paper.paper import Paper


class StandardPaper(Paper):
  '''
  Paper of a limited set:
  - standardized by a standards organization (sic)
  - supported across platform by Qt
  '''
  
  def __repr__(self):
    ''' 
    Human readable description including name, dimensions in mm. 
    
    !!! Not oriented
    '''
    return self.name + " " + self._normalSizeString

    
  @property
  def _normalSizeString(self):
    " string for normalized size  "
    size = self.integralNormalSizeMM
    return str(size.width()) + 'x' + str(size.height()) + 'mm'
  
  
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
  
  
  
  @property
  def integralNormalSizeMM(self):
    '''
    QSize
    - normalized (width < height)
    - integral
    - units mm
    '''
    result = Paper.sizeModel[self.paperEnum]
    assert isinstance(result, QSize)
    assert result.width() <= result.height()
    return result
  
  
  '''
  Oriented and Normal are two opposing choices:
  Oriented: width may be greater than height.
  Normal: width less than or equal to height.
  Caller must insure the passed size has the same property, oriented or normal.
  '''
  
  def isOrientedSizeEpsilonEqual(self, orientation, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    integralOrientedSize = self.integralOrientedSizeMM(orientation)
    result = StandardPaper._sizesEpsilonEqual(integralOrientedSize, sizeF)
    return result
  
  
  def isNormalSizeEpsilonEqual(self, sizeF):
    assert isinstance(sizeF, QSizeF)  # and is millimeter units
    integralSize = self.integralNormalSizeMM
    result = StandardPaper._sizesEpsilonEqual(integralSize, sizeF)
    return result
  
  @classmethod
  def _sizesEpsilonEqual(cls, size1, size2):
    result = abs(size1.width() - size2.width()) < 0.5 \
            and abs(size1.height() - size2.height()) < 0.5
    return result
    
    
    
  @property
  def isStandard(self):
    '''
    Implement deferred
    '''
    return True

  
  
  
