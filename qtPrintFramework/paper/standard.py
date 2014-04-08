'''
'''

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import QSize

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
    return  Paper.nameModel[self.pageSize]
  
  
  '''
  paperSize(self) inherited, but its an enum, not a size
  '''
  
  '''
  Only StandardPaper has size.
  '''
  
  def orientedSizeMM(self, orientation):
    '''
    QSize oriented
    '''
    if orientation == QPrinter.Portrait:
      result = self.integralSizeMM
    else:
      result = Paper._normalizedPaperSize(self.integralSizeMM)
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
    Implement deferred
    '''
    return True

  
  
  
