
'''
!!! NOT depend on QtPrintSupport printing subsystem

Use on mobile platforms where QtPrintSupport is not compiled.
Or use while Qt print framework has bugs re systems without real printers on certain platforms (Linux.)
'''

from PyQt5.QtCore import QSizeF

from qtPrintFramework.converser.converser import Converser
from qtPrintFramework.pageLayout.components.paper.standard import StandardPaper



class UnprinteredConverser(Converser):
  '''
  A Converser subclass that has NO real printer.
  
  Does NOT need QtPrintSupport.
  Uses non-native dialogs provided by this framework.
  '''
  
  def conversePageSetup(self):
    '''
    Implement deferred.
    '''
    self.conversePageSetupNonNative()
      
      
  def conversePrint(self):
    '''
    Implement deferred.
    
    Use this framework's dialog and implementation of 'printing' (to a file.)
    '''
    print("Not implemented")
  
  
  def setCurrentFrameworkPageSetupDialog(self):
    '''
    Set current page setup dialog to:
    a non-native dialog independent of print subsystem and OS.
    '''
    self.currentFrameworkPageSetupDialog = self.toFilePageSetupDialog
  
  
  def printablePageSizeInch(self):
    '''
    Implement deferred.
    
    Specialize: return what user chose in PageSetup dialog
    '''
    #TODO get from PageLayout
    # TEMP Hack: return fixed size
    result = QSizeF(8.5, 11)
    self._checkPrintablePageSizeInch(result)
    return result
  
  
  def paper(self):
    '''
    Implement deferred.
    
    Specialize: return what user chose in PageSetup dialog
    '''
    # TEMP hack: return fixed paper
    result = StandardPaper(1)
    return result
  
  
  
  '''
  Implement deferred methods that capture/propagate
  between dialog and printerAdaptor.
  '''
  """
  TODO Never called.
  def _capturePageSetupChange(self):
    
    OLD
    oldPageSetup = copy(self.pageLayout)
    self.pageLayout.fromPrinterAdaptor(self.printerAdaptor)
    if not oldPageSetup == self.pageLayout:
      self._emitUserChangedPaper()
    self.pageLayout.warnIfDisagreesWithPrinterAdaptor(self.printerAdaptor)
  """

  def _propagateChangedPageSetup(self):
    '''
    No other object is interested.
    '''
    pass
    

  
