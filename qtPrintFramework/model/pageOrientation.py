
from PyQt5.QtGui import QPageLayout

from qtPrintFramework.model.adaptedModel import AdaptedModel
from qtPrintFramework.orientation import Orientation

class AdaptedPageOrientationModel(AdaptedModel):
  '''
  '''
    
  def _createValues(self, printerAdaptor=None):   # printerAdaptor not used
    ''' See super. '''
    '''
    Dictionary keyed by names of paper orientations, of enum values.
    For all paper orientations in QPageLayout enum (not what current printer supports.)
    '''
    
    """
    This works but is untranslated:
    
    self.values = AdaptedModel._getAdaptedDictionary(enumOwningClass=QPageLayout, 
                                                     enumType=QPageLayout.Orientation)
    """
    
    '''
    This is less flexible, doesn't capture Qt's values automatically.
    But is i18n
    '''
    self.values = {Orientation(QPageLayout.Portrait).name : QPageLayout.Portrait,
                   Orientation(QPageLayout.Landscape).name : QPageLayout.Landscape
                   }
    
