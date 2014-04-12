

from qtPrintFramework.paper.paper import Paper
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport


class CustomPaper(Paper):
  '''
  Paper with an unknown size.
  Represents a singleton thing, but actually many instances may exist.
  '''
  
  def __init__(self):
    self.paperEnum = QPagedPaintDevice.Custom
    
    
  def __repr__(self):
    ''' Human readable description'''
    return self.name + " Unknown size"
  
  
  @property
  def name(self):
    '''
    Don't use model.  We might eliminate the enum from the model.  Always 'Custom'
    '''
    return  'Custom'
  
  
  '''
  paperEnum attribute inherited
  '''

  '''
  !!! No size methods.  Undefined.
  '''
  
  @property
  def isStandard(self):
    '''
    Reimplement super
    '''
    return False

  
  
  
