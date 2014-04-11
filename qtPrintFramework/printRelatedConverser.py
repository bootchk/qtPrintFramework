'''
'''

from copy import copy

from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrintDialog

from PyQt5.QtCore import pyqtSignal as Signal

from qtPrintFramework.userInterface.printerlessPageSetupDialog import PrinterlessPageSetupDialog
from qtPrintFramework.pageSetup import PageSetup


class PrintConverser(QObject):
  '''
  Knows how to conduct conversations about printers:
  - print
  - page setup
  
  Knows parentWidget of dialogs.
  Hides modality of dialogs.
  
  This does NOT hide non-native/native distinction.  
  PrinterAdaptor also knows distinction, and dispatches to here.
  TODO should this be two subclasses?  Then pageSetup could not be owned here.
  '''
  
  
  '''
  Meaning of signals:
  userChangedPaper is 
  
  Algebra of signals:
  
  userChangedPrinter and userChangedPaper are emitted before other signals
  
  userChangedPrinter and userChangedPaper are NOT emitted unless there is a change 
  (not emitted if user is offered choice but OK's when choice is same as previous.)
  
  userChangedPrinter and userChangedPaper are NOT emitted if userCanceledPrintRelatedConversation is emitted
  
  userAcceptedFoo and userCanceledPrintRelatedConversation are mutually exclusive
  '''
  userChangedPaper = Signal()
  
  userAcceptedPrint = Signal()
  userAcceptedPageSetup = Signal()
  userAcceptedPrintPDF = Signal()
  
  userCanceledPrintRelatedConversation = Signal()
  
  '''
  FUTURE
  userChangedPrinter = Signal()
  Not necessary since user must print to change printers.
  Assume apps do not have a separate 'Choose Printer' action.
  If user changes printers using System Preferences,
  we can't know of it?  (App can get signal elsewhere?)
  OR
  PageSetup allows user to change printer?
  '''
  
  
  
  
  def __init__(self, parentWidget, printerAdaptor):
    super(PrintConverser, self).__init__()
    self.parentWidget = parentWidget
    
    self.printerAdaptor = printerAdaptor  # TODO really need this here?
    
    # self owns because self mediates use of it: every conversation
    self.pageSetup = PageSetup(printerAdaptor)


  '''
  Page setup
  '''
    
  def conversePageSetupNonNative(self, printerAdaptor):
    '''
    User our own dialog, which works with non-native printers (on some platforms?)
    '''
    print("NonNative page setup")
    dialog = PrinterlessPageSetupDialog(pageSetup=self.pageSetup, parentWidget=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self._acceptNonNativePageSetupSlot)
    # execution continues but conversation not complete
    
    
    
  def conversePageSetupNative(self, printerAdaptor):
    '''
    Use QPageSetup dialog, which works with native printers.
    
    Here, the native dialog remembers page setup.
    We don't pass a PageSetup.
    Native dialog correctly shows user's last choices for printer, page setup.
    '''
    print("Opening page setup dialog")
    print(printerAdaptor.description)
    
    assert printerAdaptor.isValid()
    assert printerAdaptor.isAdaptingNative()
    assert self.parentWidget is not None
    
    dialog = QPageSetupDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self._acceptNativePageSetupSlot)
    
    
  '''
  Print
  '''
    
  def conversePrintNative(self, printerAdaptor):
    
    print("Native print to", printerAdaptor.description)
    
    dialog = QPrintDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self._acceptNativePrintSlot)
    
    
  def conversePrintNonNative(self, printerAdaptor):
    '''
    Print to a non-native printer.
    On Win, action PrintPDF comes here
    '''
    print("NonNative print to", printerAdaptor.description)
    # TODO
    # This dialog will be a file chooser with PageSetup?
    #self._showPrintRelatedDialogWindowModal(dialog)
    self._printerAdaptor = printerAdaptor
    self._acceptNonNativePrintSlot() # TEMP assume accepted


  '''
  Common code, and signal handlers.
  '''

  def _showPrintRelatedDialogWindowModal(self, dialog, model, acceptSlot):
    '''
    Show a print related dialog in dialog mode:
    - appropriate for platform (window-modal)
    - appropriate for document-related actions (sheets on OSX.)
    '''
    self._printerAdaptor = model  # remember for local use
    dialog.accepted.connect(acceptSlot)
    dialog.rejected.connect(self._cancelSlot)
    dialog.open() # window modal
    
  

  def _acceptNativePrintSlot(self):
    '''
    A native PrintDialog was accepted.
    User may have changed real printer and/or it's page setup.
    
    Whether native printer or non-native printer (user changed printer)
    reflect user's choices into PageSetup.
    '''
    self._capturePageSetupChange()
    print("Accept native print dialog on", self._printerAdaptor.description)
    self.userAcceptedPrint.emit()


  def _acceptNonNativePrintSlot(self):
    '''
    A nonnative PrintDialog was accepted.
    User does not have choices for printer, but by choosing this action, makes 'PDF' the current printer?
    User may have changed it's page setup.
    User may have chosen a new file.
    
    Whether native printer or non-native printer (user changed printer)
    reflect user's choices into PageSetup.
    '''
    self._capturePageSetupChange()
    print("Accept non-native print dialog on", self._printerAdaptor.description)
    self.userAcceptedPrintPDF.emit()


  def _acceptNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    User may have changed real printer and/or it's page setup.
    
    TODO are the semantics the same on all platforms?
    or do some platforms not allow user to choose a new printer (make it current.)
    '''
    self._capturePageSetupChange()
    print("Accept native page setup dialog on", self._printerAdaptor.description)
    self.userAcceptedPageSetup.emit()
  
  
  def _capturePageSetupChange(self):
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromPrinterAdaptor(self.printerAdaptor)
    if not oldPageSetup == self.pageSetup:
      self.userChangedPaper.emit()
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)
    

  def _acceptNonNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    
    Dialog does not allow user to change adapted printer.
    User might have changed page setup.
    
    PageSetup control/view has user's choices,
    but they have not been applied to a PrinterAdaptor.)
    '''
    print("Before accept nonnative page setup", self._printerAdaptor.description)
    
    # !!! This is similar, but not the same as _capturePageSetupChange()
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromControlView()
    if not oldPageSetup == self.pageSetup:
      self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
      self.userChangedPaper.emit()
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)
    
    print("After accept nonnative page setup", self._printerAdaptor.description)
    self.userAcceptedPageSetup.emit()
    
    
  def _cancelSlot(self):
    '''
    PageSetupDialog or PrintDialog was canceled.
    
    No choices made by user are kept:
    - printerAdaptor still adapts same printer
    - pageSetup of adapted printer is unchanged.
    '''
    self.pageSetup.toControlView()  # restore view to equal unchanged model
    self.userCanceledPrintRelatedConversation.emit()
    
    

