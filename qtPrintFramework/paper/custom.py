
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.paper.paper import Paper


class CustomPaper(Paper):
  '''
  Paper that knows its unique user-defined size (not from a model).
  
  Currently, CustomPaper only comes from native dialogs, when size is definitely known at creation time.
  We can change this design when we add GUI to let user define size in non-native PageSetupDialog.
  '''
  
  def __init__(self, integralOrientedSizeMM, orientation):
    self.paperEnum = QPagedPaintDevice.Custom
    
    '''
    !!! Keep portrait size.
    Is NOT an assertion that size is normalized.
    '''
    assert isinstance(integralOrientedSizeMM, QSize)
    assert orientation == 0 or orientation == 1
    self._portraitSizeMM = OrientedSize.portraitSizeMM(integralOrientedSizeMM, orientation)

    
  # Inherited: def __repr__(self):
  
  
  @property
  def name(self):
    '''
    Don't use model.  We might eliminate the enum from the model.  Always 'Custom'
    '''
    return  'Custom'
  
  @classmethod
  def defaultSize(cls):
    '''
    Size when user has chosen Custom but not specified dimensions
    (In non-native PageSetup dialog that doesn't have capability to specify dimensions.)
    '''
    return QSize(640, 480)
  
  
  '''
  paperEnum attribute inherited
  '''

  @property
  def integralNormalSizeMM(self):
    '''
    !!! Hack.  The name says Normal, but it ain't necessarily so.
    
    Called by Paper.integralOrientedSizeMM()
    '''
    return self._portraitSizeMM
  
  
  
  @property
  def isStandard(self):
    '''
    Reimplement super
    '''
    return False

  
  
  
