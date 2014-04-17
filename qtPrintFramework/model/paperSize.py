


from PyQt5.QtGui import QPagedPaintDevice # !! Not in QtPrintSupport

from qtPrintFramework.model.adaptedModel import AdaptedSortedModel


class AdaptedPaperSizeModel(AdaptedSortedModel):  # !!! Sorted
  '''
  '''
    
  def _createValues(self):
    ''' See super. '''
    '''
    Dictionary keyed by names of paper sizes, of enum values.
    For all paper sizes in QPagedPaintDevice enum.
    
    A current printer might support a different set.
    Typically a subset.
    When a superset: Custom?
    
    TODO del Custom
    '''
    self.values = AdaptedSortedModel._getAdaptedDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion



PaperSizeModel = AdaptedPaperSizeModel()