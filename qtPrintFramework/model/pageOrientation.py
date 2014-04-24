'''
'''
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.model.adaptedModel import AdaptedModel


class AdaptedPageOrientationModel(AdaptedModel):
  '''
  '''
    
  def _createValues(self):
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
    print("Translation:", self.tr("Portrait"))
    self.values = {self.tr("Portrait"):QPrinter.Portrait,
                   self.tr("Landscape"):QPrinter.Landscape
                   }
    
