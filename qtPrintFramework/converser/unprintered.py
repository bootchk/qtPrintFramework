

'''
!!! NOT depend on QtPrintSupport printing subsystem

Use on mobile platforms where QtPrintSupport is not compiled.
Or use while Qt print framework has bugs re systems without real printers on certain platforms (Linux.)
'''

from qtPrintFramework.converser.converser import Converser

from qtPrintFramework.pageSetup.printerlessPageSetup import PrinterlessPageSetup
from qtPrintFramework.userInterface.dialog.printerlessPageSetup import PrinterlessPageSetupDialog

# from qtPrintFramework.alertLog import debugLog, alertLog


class UnprinteredConverser(Converser):
  '''
  A Converser that has NO real printer.
  
  Does NOT need QtPrintSupport.
  Uses dialogs provided by this framework
  '''
  def __init__(self, parentWidget):
    super(UnprinteredConverser, self).__init__(parentWidget)
    
    # Specialized
    self._getUnprinteredPageSetupAndDialog(parentWidget)



  def _getUnprinteredPageSetupAndDialog(self, parentWidget):
    '''
  
    '''
    
    '''
    Static dialog owned by this framework.
    Requires no knowledge of printerAdaptor or current printer.
    '''
    self.toFilePageSetupDialog = PrinterlessPageSetupDialog(parentWidget=self.parentWidget)
    
    '''
    self owns because self mediates use of it on every conversation.
    
    PageSetup is initialized from settings OR printerAdaptor.
    '''
    self.pageSetup = PrinterlessPageSetup(masterEditor=self.toFilePageSetupDialog)
    
  
  def conversePageSetup(self):
    '''
    Implement deferred.
    '''
    self.conversePageSetupNonNative()
      
      
  def conversePrint(self):
    '''
    Implement deferred.
    
    Use this framework's dialog and implementation of 'printing'
    '''
    print("Not implemented")
  
  
  def setCurrentFrameworkPageSetupDialog(self):
    self.currentFrameworkPageSetupDialog = self.toFilePageSetupDialog
  
  
  def printablePageSizeInch(self):
    '''
    QSizeF that is:
    - not empty (both w and h > 0)
    else InvalidPageSize.
    
    Units Inch
    
    Assert not empty implies isValid, which is both w and h >= 0.
    
    Exported because app may wish to know page size even if not printing.
    '''
    result = self.printerAdaptor.printablePageSizeInch()
    self._checkPrintablePageSizeInch(result)
    return result
  
  
  def paper(self):
    '''
    Specialize: delegate to printerAdaptor.
    '''
    return self.printerAdaptor.paper()
  
  
  
    
  """
  def _acceptNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    User may have changed real printer and/or it's page setup.
    
    TODO are the semantics the same on all platforms?
    or do some platforms not allow user to choose a new printer (make it current.)
    '''
    self.dump("Accept native page setup, printerAdaptor before setting it ")
    self._capturePageSetupChange()
    self.dump("accept native page setup, printerAdaptor after setting it")
    
    self.userAcceptedPageSetup.emit()
    debugLog("Emit userAcceptedPageSetup")
  
    self.pageSetup.toSettings()
  """ 
  
  '''
  Implement deferred methods that capture/propagate
  between dialog and printerAdaptor.
  '''
  """
  TODO Never called.
  def _capturePageSetupChange(self):
    
    OLD
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromPrinterAdaptor(self.printerAdaptor)
    if not oldPageSetup == self.pageSetup:
      self._emitUserChangedPaper()
    self.pageSetup.warnIfDisagreesWithPrinterAdaptor(self.printerAdaptor)
  """

  def _propagateChangedPageSetup(self):
    '''
    No other object is interested.
    '''
    pass
    

