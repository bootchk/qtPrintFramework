


from PyQt5.QtPrintSupport import QPrinter, QPrinterInfo
from PyQt5.QtGui import QPagedPaintDevice # !! Not in QtPrintSupport

from qtPrintFramework.model.adaptedModel import AdaptedSortedModel


class PrinterPaperSizeModel(AdaptedSortedModel):  # !!! Sorted
  '''
  Model derived from a real printer.
  
  Show only paper sizes printer supports.
  If model has paper sizes that printer NOT support, when user chooses an unsupported value,
  and setPaperSize() is called, printer refuses to acknowledge (setPaperSize() has no effect), 
  and this framework gets out of sync with printer.
  
  Current implemntation omits all Custom page sizes.
  '''
    
  def _createValues(self, printerAdaptor):
    ''' See super. '''
    '''
    Dictionary keyed by names of paper sizes, of enum values.
    For all paper sizes reported by printer AND in QPagedPaintDevice enum AND not Custom.
    So this is a subset of Qt's enum.
    
    !!! Alternate design: Custom is in model.
    Here, we are excluding it from this model used only by the framework's Page Setup PDF dialog.
    
    !!! No i18n for paper names: assume names are internationally recognized.
    '''
    self.values = self._valuesFromPrinter(printerAdaptor)
    assert 'Custom' not in self.values
    


  def _valuesFromPrinter(self, printerAdaptor):
    '''
    Create model including only those values reported by adapted printer.
    
    If adapted printer is a PDF printer, includes all values known to Qt?  TODO 
    '''
    result = {}
    
    qtModel = self._qtReverseModel()
    
    printerInfo = QPrinterInfo(printerAdaptor)
    printerPaperSizes = printerInfo.supportedPaperSizes()
    for paperSizeEnum in printerPaperSizes:
      #print paperSizeEnum
      
      if paperSizeEnum == QPrinter.Custom:
        # Omit custom.  Why? lazy implementation or impossible to reverse?
        continue
      elif paperSizeEnum in qtModel:
        # paperSizeEnum known to Qt
        result[qtModel[paperSizeEnum]] = paperSizeEnum
      else:
        print("Printer reports paper size unknown to Qt.")
        # omit
    
    assert len(result) > 0  # TODO a warning here
    return result
  
  
  def _qtReverseModel(self):
    '''
    Get dictionary of (enum, name) from Qt enumerated type.
    '''
    return AdaptedSortedModel._getAdaptedReverseDictionary(enumOwningClass=QPagedPaintDevice, 
                                                     enumType=QPagedPaintDevice.PageSize)