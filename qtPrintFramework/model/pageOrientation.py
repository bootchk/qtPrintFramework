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
    self.values = AdaptedModel._getAdaptedDictionary(enumOwningClass=QPrinter, 
                                                     enumType=QPrinter.Orientation)

PageOrientationModel = AdaptedPageOrientationModel()