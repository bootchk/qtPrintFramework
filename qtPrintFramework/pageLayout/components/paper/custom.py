
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.pageLayout.components.paper.paper import Paper
from qtPrintFramework.pageLayout.components.orientation import Orientation


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
    assert isinstance(orientation, Orientation)
    self.setSize(integralOrientedSizeMM, orientation)
    ## WAS, EQUIVALENT: self._portraitSizeMM = OrientedSize.portraitSizeMM(integralOrientedSizeMM, orientation)

    
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

  def setSize(self, integralOrientedSizeMM, orientation):
    '''
    Set self size by orientedIntegralSize, orientation.
    
    A user can set size of Custom paper via native Print dialog.
    Also used to init a Custom paper when user uses non-native PageSetup dialog.
    '''
    self._portraitSizeMM = OrientedSize.portraitSizeMM(integralOrientedSizeMM, orientation)
    
  
  @property
  def integralDefinedSizeMM(self):
    '''
    Called by Paper.integralOrientedSizeMM()
    '''
    return self._portraitSizeMM
  
  
  
  @property
  def isStandard(self):
    '''
    Reimplement super
    '''
    return False


  def hasEqualSizeTo(self, other):
    result = self.integralDefinedSizeMM == other.integralDefinedSizeMM
    return result
  
  
