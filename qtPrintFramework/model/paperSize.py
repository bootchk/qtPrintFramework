


from PyQt5.QtGui import QPagedPaintDevice # !! Not in QtPrintSupport

from qtPrintFramework.model.adaptedModel import AdaptedModel


class AdaptedPaperSizeModel(AdaptedModel):
  '''
  '''
    
  def _createValues(self):
    ''' See super. '''
    '''
    Dictionary keyed by names of paper sizes, of enum values.
    For all paper sizes in QPagedPaintDevice enum (not what current printer supports.)
    '''
    self.values = AdaptedModel._getAdaptedDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion



PaperSizeModel = AdaptedPaperSizeModel()