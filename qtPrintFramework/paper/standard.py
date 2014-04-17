

from PyQt5.QtCore import QSize

from qtPrintFramework.paper.paper import Paper


class StandardPaper(Paper):
  '''
  Paper of a limited set:
  - standardized by a standards organization (sic)
  - supported across platform by Qt
  '''
  
  # Inherited def __repr__(self):
  
  
  @property
  def name(self):
    '''
    Implement deferred.
    '''
    return  Paper.nameModel[self.paperEnum]
  
  
  '''
  paperEnum attribute inherited
  '''
  
  
  @property
  def integralNormalSizeMM(self):
    '''
    Specialize Paper:  size is constant from a defining, standard model.
    QSize
    - normalized (width < height)
    - integral
    - units mm
    '''
    result = Paper.sizeModel[self.paperEnum]
    assert isinstance(result, QSize)
    assert result.width() <= result.height()
    return result
    
    
    
    
  @property
  def isStandard(self):
    '''
    Implement deferred
    '''
    return True

  
  
  
