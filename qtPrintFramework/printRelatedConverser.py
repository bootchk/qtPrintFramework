'''
'''

from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrintDialog


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
  
  
  def __init__(self, parentWidget, printerAdaptor):
    super(PrintConverser, self).__init__()
    self.parentWidget = parentWidget
    
    self.printerAdaptor = printerAdaptor  # TODO really need this here?
    
    # self owns because self mediates use of it: every conversation
    self.pageSetup = PageSetup(printerAdaptor)


  '''
  Page setup
  '''
    
  def doPageSetupNonNative(self, printerAdaptor):
    '''
    User our own dialog, which works with non-native printers (on some platforms?)
    '''
    print("NonNative page setup")
    dialog = PrinterlessPageSetupDialog(pageSetup=self.pageSetup, parentWidget=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self.acceptNonNativePageSetupSlot)
    # execution continues but conversation not complete
    
    
    
  def doPageSetupNative(self, printerAdaptor):
    '''
    Use QPageSetup dialog, which works with native printers.
    
    Here, the native dialog remembers page setup.
    We don't pass a PageSetup.
    Native dialog correctly shows user's last choices for printer, page setup.
    '''
    print("Opening page setup dialog")
    printerAdaptor.describePrinter()
    
    assert printerAdaptor.isValid()
    assert printerAdaptor.isAdaptingNative()
    assert self.parentWidget is not None
    
    dialog = QPageSetupDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self.acceptNativePageSetupSlot)
    
    
  '''
  Print
  '''
    
  def doPrintNative(self, printerAdaptor):
    
    print("Native print")
    printerAdaptor.describePrinter()
    
    dialog = QPrintDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor, acceptSlot=self.acceptNativePrintSlot)
    
    
  def doPrintNonNative(self, printerAdaptor):
    '''
    Print to a non-native printer.
    On Win, action PrintPDF comes here
    '''
    print("NonNative print")
    # TODO
    #self._showPrintRelatedDialogWindowModal(dialog)



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
    dialog.rejected.connect(self.cancelSlot)
    dialog.open() # window modal
    
  

  def acceptNativePrintSlot(self):
    '''
    A native PrintDialog was accepted.
    User may have changed real printer and/or it's page setup.
    
    Whether native printer or non-native printer (user changed it)
    reflect user's choices into PageSetup.
    '''
    print("Accept native print dialog")
    self._printerAdaptor.describePrinter()
    
    self.pageSetup.fromPrinterAdaptor(self.printerAdaptor)
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)


  def acceptNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    User may have changed real printer and/or it's page setup.
    
    TODO are the semantics the same on all platforms?
    or do some platforms not allow user to choose a new printer (make it current.)
    '''
    # Same semantics as Print
    self.acceptNativePrintSlot()
    

  def acceptNonNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    
    Dialog does not allow user to change adapted printer.
    User might have changed page setup.
    
    PageSetup control/view has user's choices,
    but they have not been applied to a PrinterAdaptor.)
    '''
    self._printerAdaptor.describePrinter()  # Before we change it
    
    self.pageSetup.fromControlView()
    self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
    
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)
    self._printerAdaptor.describePrinter()  # After we changed it
    
    
  def cancelSlot(self):
    '''
    PageSetupDialog or PrintDialog was canceled.
    
    No choices made by user are kept:
    - printerAdaptor still adapts same printer
    - pageSetup of adapted printer is unchanged.
    '''
    self.pageSetup.toControlView()  # restore view to equal unchanged model
    print('canceled')
    pass
    

