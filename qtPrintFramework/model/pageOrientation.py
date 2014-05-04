'''
'''
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.model.adaptedModel import AdaptedModel
from qtPrintFramework.orientation import Orientation

class AdaptedPageOrientationModel(AdaptedModel):
  '''
  '''
    
  def _createValues(self, printerAdaptor=None):   # printerAdaptor not used
    ''' See super. '''
    '''
    Dictionary keyed by names of paper orientations, of enum values.
    For all paper orientations in QPrinter enum (not what current printer supports.)
    '''
    
    """
    This works but is untranslated:
    
    self.values = AdaptedModel._getAdaptedDictionary(enumOwningClass=QPrinter, 
                                                     enumType=QPrinter.Orientation)
    """
    
    '''
    This is less flexible, doesn't capture Qt's values automatically.
    But is i18n
    '''
    self.values = {Orientation(QPrinter.Portrait).name : QPrinter.Portrait,
                   Orientation(QPrinter.Landscape).name : QPrinter.Landscape
                   }
    
