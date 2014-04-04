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
    self.pageSetup = PageSetup()


  '''
  Page setup
  '''
    
  def doPageSetupNonNative(self, printerAdaptor):
    '''
    User our own dialog, which works with non-native printers (on some platforms?)
    '''
    print("NonNative page setup")
    dialog = PrinterlessPageSetupDialog(pageSetup=self.pageSetup, parentWidget=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor)
    # execution continues but conversation not complete
    
    
    
  def doPageSetupNative(self, printerAdaptor):
    '''
    Use QPageSetup dialog, which works with native printers.
    '''
    print("Opening page setup dialog")
    print("On printer named:", printerAdaptor.printerName())
    print("Whose paper size is:", printerAdaptor.paperSize())
    
    assert printerAdaptor.isValid()
    assert printerAdaptor.isAdaptingNative()
    assert self.parentWidget is not None
    
    dialog = QPageSetupDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor)
    
    
  '''
  Print
  '''
    
  def doPrintNative(self, printerAdaptor):
    
    print("Native print")
    dialog = QPrintDialog(printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, model=printerAdaptor)
    
    
  def doPrintNonNative(self, printerAdaptor):
    print("NonNative print")
    #self._showPrintRelatedDialogWindowModal(dialog)



  

  def _showPrintRelatedDialogWindowModal(self, dialog, model):
    self._printerAdaptor = model  # remember for local use
    dialog.accepted.connect(self.acceptSlot)
    dialog.rejected.connect(self.acceptSlot)  # TODO cancelslot
    dialog.open() # window modal
    
  
  # TODO different slots for print, page setup, cancel
  # page setup sends to printerAdaptor
  # print gets from printerAdaptor
  def acceptSlot(self):
    print('accepted or canceled')
    self._printerAdaptor.describePrinter()
    self.pageSetup.dump()
    self.pageSetup.toPrinterAdaptor(self.printerAdaptor)



