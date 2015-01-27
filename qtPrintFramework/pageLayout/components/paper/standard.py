
from PyQt5.QtCore import QSize

from qtPrintFramework.pageLayout.components.paper.paper import Paper


class StandardPaper(Paper):
  '''
  Paper of a limited set:
  - standardized by a standards organization (sic)
  - supported across platform by Qt
 
  Inherited:
   -  __repr__
   - value
   
  Should be registered with QML if using QML.
  '''
  
  def __init__(self, initialValue):
    super().__init__(initialValue)
    
  
  @property
  def name(self):
    '''
    Implement deferred.
    '''
    return  Paper.nameModel[self.value]
  
  
  @property
  def integralDefinedSizeMM(self):
    '''
    Specialize Paper:  size is constant from a defining, standard model.
    QSize
    - 
    - integral
    - units mm
    '''
    result = Paper.sizeModel[self.value]
    assert isinstance(result, QSize)
    ## Not necessarily normalized (width < height)
    ## assert result.width() <= result.height()
    return result
    
    
  @property
  def isStandard(self):
    '''
    Implement deferred
    '''
    return True

  
  
  
