
'''
!!! NOT depend on QtPrintSupport printing subsystem

Use on mobile platforms where QtPrintSupport is not compiled.
Or use while Qt print framework has bugs re systems without real printers on certain platforms (Linux.)
'''

from PyQt5.QtCore import QSizeF

from qtPrintFramework.converser.converser import Converser
from qtPrintFramework.pageSetup.printerlessPageSetup import PrinterlessPageSetup
from qtPrintFramework.paper.standard import StandardPaper
# from qtPrintFramework.alertLog import debugLog, alertLog

import qtPrintFramework.config as config
# Dynamic imports below for QML/QWidget



class UnprinteredConverser(Converser):
  '''
  A Converser subclass that has NO real printer.
  
  Does NOT need QtPrintSupport.
  Uses non-native dialogs provided by this framework.
  '''
  def __init__(self, parentWidget):
    super(UnprinteredConverser, self).__init__(parentWidget)
    
    # Specialized
    self._getUnprinteredPageSetupAndDialog(parentWidget)



  def _getUnprinteredPageSetupAndDialog(self, parentWidget):
    '''
    Create a PageSetup and a view (GUI dialog) on it.
    '''
    '''
    Static dialog owned by this framework.
    Requires no knowledge of printerAdaptor or current printer.
    '''
    if config.useQML:
      from qtPrintFramework.userInterface.qml.dialog.pageSetupDialogQML import pageSetupDialogMgr

      self.toFilePageSetupDialog = pageSetupDialogMgr.pageSetupDialogDelegate()
    else: # QWidget
      from qtPrintFramework.userInterface.widget.dialog.printerlessPageSetup import PrinterlessPageSetupDialog

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
    #TODO get from PageSetup
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
    

  
