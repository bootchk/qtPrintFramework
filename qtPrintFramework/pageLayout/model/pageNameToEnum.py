


from PyQt5.QtGui import QPagedPaintDevice # !! Not in QtPrintSupport

from qtPrintFramework.pageLayout.model.adaptedModel import AdaptedSortedModel


class AdaptedPageNameToEnumModel(AdaptedSortedModel):  # !!! Sorted
  '''
  Dictionary from name to page enum.
  
  From Qt's enum.
  Static, a fixed set for use with paperless printers (PDF) that can 'print' to any size you specify.
  '''
    
  def _createValues(self, printerAdaptor=None):
    ''' See super. '''
    '''
    Dictionary keyed by names of page sizes, of enum values.
    For all page sizes in QPagedPaintDevice enum.
    
    A current printer might support a different set.  Typically a subset.
    (Depends on physical paper loaded in physical trays.)
    
    !!! Alternate design: Custom is in model.
    Here, we are excluding it from this model used only by the framework's Page Setup PDF dialog.
    
    !!! No i18n for page names: assume names are internationally recognized.
    '''
    self.values = AdaptedSortedModel._getAdaptedDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize) # !!! Paper/Page confusion

    self._deleteCustomPaper()
    
    print(self.values)
    
    
  def _deleteCustomPaper(self):
    self.values.pop("Custom", None)


pageNameToEnumModel = AdaptedPageNameToEnumModel()  # singleton