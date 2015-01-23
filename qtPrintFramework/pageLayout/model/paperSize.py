


from PyQt5.QtGui import QPagedPaintDevice # !! Not in QtPrintSupport

from qtPrintFramework.pageLayout.model.adaptedModel import AdaptedSortedModel


class AdaptedPaperSizeModel(AdaptedSortedModel):  # !!! Sorted
  '''
  PaperSizeModel from Qt's enum.
  i.e. static, a fixed set for use with paperless printers (PDF) that can 'print' to any size you specify.
  '''
    
  def _createValues(self, printerAdaptor=None):
    ''' See super. '''
    '''
    Dictionary keyed by names of paper sizes, of enum values.
    For all paper sizes in QPagedPaintDevice enum.
    
    A current printer might support a different set.
    Typically a subset.
    
    !!! Alternate design: Custom is in model.
    Here, we are excluding it from this model used only by the framework's Page Setup PDF dialog.
    
    !!! No i18n for paper names: assume names are internationally recognized.
    '''
    self.values = AdaptedSortedModel._getAdaptedDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion

    self._deleteCustomPaper()
    
    
  def _deleteCustomPaper(self):
    self.values.pop("Custom", None)


