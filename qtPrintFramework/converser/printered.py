
from copy import copy

# !!! Depends on QtPrintSupport printing subsystem
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrintDialog


from qtPrintFramework.converser.converser import Converser

from qtPrintFramework.printer.printerAdaptor import PrinterAdaptor
from qtPrintFramework.pageSetup.printeredPageSetup import PrinteredPageSetup
from qtPrintFramework.userInterface.widget.dialog.printerlessPageSetup import PrinterlessPageSetupDialog
from qtPrintFramework.userInterface.widget.dialog.realPrinterPageSetup import RealPrinterPageSetupDialog

from qtPrintFramework.alertLog import debugLog, alertLog


class PrinteredConverser(Converser):
  '''
  A Converser that cooperates with a real printer.
  Printer is provided via QtPrintSupport.
  Printer uses native dialogs (provided by OS, not Qt.)
  '''
  def __init__(self, parentWidget):
    super(PrinteredConverser, self).__init__(parentWidget)
    
    # Specialized
    self._getPrinteredPageSetupAndDialog(parentWidget)



  def _getPrinteredPageSetupAndDialog(self, parentWidget):
    '''
    PrintConverser has-a PrinterAdaptor (unidirectional link.)
    See below, this is used in signal handlers.
    '''
    self.printerAdaptor = PrinterAdaptor(parentWidget=parentWidget)
    
    '''
    Static dialog owned by this framework.
    Requires no knowledge of printerAdaptor or current printer.
    '''
    self.toFilePageSetupDialog = PrinterlessPageSetupDialog(parentWidget=self.parentWidget)
    
    '''
    self owns because self mediates use of it on every conversation.
    
    PageSetup is initialized from settings OR printerAdaptor.
    '''
    self.pageSetup = PrinteredPageSetup(masterEditor=self.toFilePageSetupDialog, printerAdaptor=self.printerAdaptor, )
    
    '''
    Not assert that printerAdaptor equal PageSetup.
    Try to make them equal now.
    '''
    self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
    '''
    Still not assert that printerAdaptor equal PageSetup, since adapted printer might not support.
    Usually they are equal.  But user might have changed system default printer.
    '''
  
  def conversePageSetup(self):
    '''
    Implement deferred.
    '''
    if self.printerAdaptor.isAdaptingNative():
      self._conversePageSetupNative()
    else:
      self.conversePageSetupNonNative()
      
      
  def conversePrint(self):
    '''
    Implement deferred.
    
    Use native print dialog.
    
    On all desktop platforms, the native print dialog supports a paperless printer (PDF or XPS.)
    Native print dialog does not imply the printer is a real printer (not paperless.)
    Native dialog is a different concept than native printer.
    
    On OSX, user using native print dialog and choosing print to PDF, 
    Qt DOES change QPrinter.outputFormat to non-native printer.
    This framework ensures the outputFormat is always native, so the same QPrinter can be used again.
    (Qt will not allow the native print and page setup dialogs to be used when outputFormat is non-native).
    
    AND on Win, printing to XPS ??
    
    On Linux, printing to PDF:
    DOES change the current printer to a non-native printer
    (the native print dialog can still be used, but Qt won't allow the native page setup dialog to be used.)
    
    On Win, print to PDF requires using non-native print and page setup dialogs.
    (Implemented by this framework TODO.)
    '''
    self._conversePrintNative()
  
  
  def setCurrentFrameworkPageSetupDialog(self):
    # TODO isAdaptingReal ?
    if self.printerAdaptor.isAdaptingNative():
      '''
      native printer is real printer or to file printer
      Create new dialog having title and papersizemodel from printerAdaptor.
      '''
      self.currentFrameworkPageSetupDialog = RealPrinterPageSetupDialog(parentWidget=self.parentWidget, printerAdaptor=self.printerAdaptor)
    else:
      # Use static dialog having fixed title and paperSize model from Qt
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
  
  
  def _conversePageSetupNative(self):
    '''
    Use QPageSetup dialog, which uses native dialogs and works with native printers.
    
    Here, the native dialog remembers page setup.
    We don't pass a PageSetup.
    Native dialog correctly shows user's last choices for printer, page setup.
    '''
    self.dump("Native page setup to")
    
    assert self.printerAdaptor.isValid()
    assert self.printerAdaptor.isAdaptingNative()
    assert self.parentWidget is not None
    
    self.checkInvariantAndFix()
    self.nativePageSetupDialog = QPageSetupDialog(self.printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog=self.nativePageSetupDialog,
                                            acceptSlot=self._acceptNativePageSetupSlot)
    
    
  def _conversePrintNative(self):
    
    self.dump("Native print to")
    
    self.checkInvariantAndFix()
    self.printerAdaptor.ensureReadyForNativeDialog()
    self.nativePrintDialog = QPrintDialog(self.printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog=self.nativePrintDialog, 
                                            acceptSlot=self._acceptNativePrintSlot)
    
    
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
    
  
  '''
  Implement deferred methods that capture/propagate
  between dialog and printerAdaptor.
  '''
  def _capturePageSetupChange(self):
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromPrinterAdaptor(self.printerAdaptor)
    if not oldPageSetup == self.pageSetup:
      self._emitUserChangedPaper()
    self.pageSetup.warnIfDisagreesWithPrinterAdaptor(self.printerAdaptor)

  def _propagateChangedPageSetup(self):
    self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
    self.pageSetup.warnIfDisagreesWithPrinterAdaptor(self.printerAdaptor)
    

  def checkInvariantAndFix(self):
    '''
    Check invariant (about QPrinter.paperSize() == framework's local Paper.paperEnum)
    and fix it if necessary.
    In other words, QPrinter is supposed to stay in sync with native,
    and qtPrintFramework is supposed to stay in sync with QPrinter.
    But qtPrintFramework can fix bugs in QPrinter.
    
    This ameliorates another bug on the OSX platform: PageSetup not persistent.
    (After one Print conversation, a printerAdaptor loses its page setup.)
    '''
    
    if not self.pageSetup.isStronglyEqualPrinterAdaptor(self.printerAdaptor):
      paper = self.pageSetup.paper
      alertLog('Fixing invariant by setting paperSize on QPrinter')
      debugLog(str(paper))
      # self.setPaperSize(paper.paperEnum)
      self.pageSetup.toPrinterAdaptor(printerAdaptor=self.printerAdaptor)
    
    """
    if sys.platform.startswith('darwin'):
      paper = self.pageSetup.paper
      #print('>>>> Darwin: always set inch paperSize on QPrinter', str(paper))
      '''
      Not just toPrinterAdaptor(), since printerAdaptor may agree with pageSetup,
      (on enums, and float sizes to epsilon)
      but platform native dialog may disagree with printerAdaptor.
  
      Call _toPrinterAdaptorByFloatInchSize() which might be more effective.
      '''
      self.pageSetup._toPrinterAdaptorByFloatInchSize(self.printerAdaptor)
    """
    
    self.dump("After checkInvariantAndFix")
