'''
'''
import sys
from copy import copy

from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrintDialog
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import pyqtSignal as Signal

from qtPrintFramework.printerAdaptor import PrinterAdaptor
from qtPrintFramework.userInterface.printerlessPageSetupDialog import PrinterlessPageSetupDialog
from qtPrintFramework.pageSetup import PageSetup

import qtPrintFramework.config as config



class PrintConverser(QObject):
  '''
  Knows how to conduct conversations about printers:
  - print
  - page setup
  
  Knows parentWidget of dialogs.  Hides modality of dialogs.
  
  Knows attributes of printer and page setup: delegates.
  
  Hides non-native/native printer distinction: dispatches.
  
  Implementation:
  owns a PageSetup and a PrinterAdaptor and Dialogs.
  An app owns only a PrintConverser (usually wrapped in a PrintSession, not included here.)
  
  !!! There are no circular references, otherwise you get segfaults on app quit
  because things are destroyed in the wrong order.
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
  
  
  
  
  def __init__(self, parentWidget):
    super(PrintConverser, self).__init__()
    self.parentWidget = parentWidget
    
    '''
    PrintConverser has-a PrinterAdaptor (unidirectional link.)
    See below, this is used in signal handlers.
    '''
    self.printerAdaptor = PrinterAdaptor(parentWidget=parentWidget)
    
    '''
    self owns because self mediates use of it: every conversation
    
    PageSetup is initialized from settings OR printerAdaptor.
    '''
    self.pageSetup = PageSetup(self.printerAdaptor)
    
    '''
    Not assert that printerAdaptor equal PageSetup.
    Try to make them equal now.
    '''
    self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
    '''
    Still not assert that printerAdaptor equal PageSetup, since adapted printer might not support.
    Usually they are equal.  But user might have changed system default printer.
    '''
    
  def dump(self, condition):
    if config.DEBUG:
      print(condition)
      print(self.printerAdaptor.description)


  '''
  Exported print related conversations (dispatch according to native/nonnative.)
  '''
      
  def conversePageSetup(self):
    '''
    Start a Page Setup conversation
    '''
    if self.printerAdaptor.isAdaptingNative():
      self._conversePageSetupNative()
    else:
      self._conversePageSetupNonNative()

    
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer, or in it's setup.)
    The conversation if accepted may include a change in self's state (user chose a different printer)
    AND a change in state of the adapted printer (user chose a different paper, etc.)
    
    On some platforms, user CAN choose different printer during page setup.
    '''
    
    
  def conversePrint(self):
    '''
    Start a print conversation.
    
    This understands differences by platform.
    '''
    if self.printerAdaptor.isAdaptingNative():
      self._conversePrintNative()
    else:
      if True:
        self._conversePrintNative()
      else:
        self._conversePrintNonNative()
        
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer.)
    The conversation if accepted may include a change in self's state (user chose a different printer.)
    '''
  
  
  def conversePrintPDF(self):
    '''
    Start a print PDF conversation.
    
    Only necessary on Win, where native or Qt provided dialog does not offer choice to print PDF.
    
    Optional (shortcutting the PrintDialog) on other platforms.

    Sets up self to print PDF.
    
    Conversation includes:
    - user choice of paper?  If current printer is not PDF?
    - user choice of file
    '''
    self._conversePrintNonNative()

      
      
  '''
  Page setup conversations
  '''
    
  def _conversePageSetupNonNative(self):
    '''
    User our own dialog, which works with non-native printers (on some platforms?)
    '''
    self.dump("NonNative page setup to")
    dialog = PrinterlessPageSetupDialog(pageSetup=self.pageSetup, parentWidget=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, acceptSlot=self._acceptNonNativePageSetupSlot)
    # execution continues but conversation not complete
    
    
    
  def _conversePageSetupNative(self):
    '''
    Use QPageSetup dialog, which works with native printers.
    
    Here, the native dialog remembers page setup.
    We don't pass a PageSetup.
    Native dialog correctly shows user's last choices for printer, page setup.
    '''
    self.dump("Native page setup to")
    
    assert self.printerAdaptor.isValid()
    assert self.printerAdaptor.isAdaptingNative()
    assert self.parentWidget is not None
    
    self.checkInvariantAndFix()
    dialog = QPageSetupDialog(self.printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, acceptSlot=self._acceptNativePageSetupSlot)
    
    
  '''
  Print
  '''
    
  def _conversePrintNative(self):
    
    self.dump("Native print to")
    
    self.checkInvariantAndFix()
    dialog = QPrintDialog(self.printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, acceptSlot=self._acceptNativePrintSlot)
    
    
  def _conversePrintNonNative(self):
    '''
    Print to a non-native printer.
    On Win, action PrintPDF comes here
    '''
    self.dump("NonNative print to")
    # TODO 'Win PrintPDF'
    # This dialog will be a file chooser with PageSetup?
    #self._showPrintRelatedDialogWindowModal(dialog)
    self._acceptNonNativePrintSlot() # TEMP assume accepted


  '''
  Common code, and signal handlers.
  '''

  def _showPrintRelatedDialogWindowModal(self, dialog, acceptSlot):
    '''
    Show a print related dialog in dialog mode:
    - appropriate for platform (window-modal)
    - appropriate for document-related actions (sheets on OSX.)
    '''
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
    self.dump("Accept native print dialog on")

    '''
    Ensure printable rect is valid size (not negative) and not empty (both width and height zero.)
    This may happen if user specifies a small Custom paper and large margins.
    Handler for print requires this, else may throw an exception e.g. for division by zero.
    '''
    size = self.printerAdaptor.printablePageSize
    if size.isValid() and not size.isEmpty():
      self.userAcceptedPrint.emit()
      if config.DEBUG:
        print("Emit userAcceptedPrint")
    else:
      _ = QMessageBox.warning(self.parentWidget,
                           "",  # title
                           "Printable page size is too small to print.  Please increase paper size or decrease margins.")  # text
      # Not emit
    


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
    self.dump("Accept non-native print dialog on")

    self.userAcceptedPrintPDF.emit()
    if config.DEBUG:
      print("Emit userAcceptedPrintPDF")


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
    if config.DEBUG:
      print("Emit userAcceptedPageSetup")
  
  
  def _capturePageSetupChange(self):
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromPrinterAdaptor(self.printerAdaptor)
    if not oldPageSetup == self.pageSetup:
      self._emitUserChangedPaper()
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)
    

  def _acceptNonNativePageSetupSlot(self):
    '''paperSizeMM
    User accepted NonNative PageSetupDialog.
    
    Dialog does not allow user to change adapted printer.
    User might have changed page setup.
    
    PageSetup control/view has user's choices,
    but they have not been applied to a PrinterAdaptor.)
    '''
    self.dump("accept nonnative page setup, printerAdaptor before setting it")
    
    # !!! This is similar, but not the same as _capturePageSetupChange()
    # Here, user made change in a non-native dialog that hasn't yet affected printerAdaptor
    oldPageSetup = copy(self.pageSetup)
    self.pageSetup.fromControlView()
    if not oldPageSetup == self.pageSetup:
      self.pageSetup.toPrinterAdaptor(self.printerAdaptor)
      self._emitUserChangedPaper()
    assert self.pageSetup.isEqualPrinterAdaptor(self.printerAdaptor)
    
    self.dump("accept nonnative page setup, printerAdaptor after setting it")

    self.userAcceptedPageSetup.emit()
    if config.DEBUG:
      print("Emit userAcceptedPageSetup")
    
    
  def _emitUserChangedPaper(self):
    '''
    User has chosen a new paper, either in Print or PageSetup dialog.
    '''
    # Tell the app
    self.userChangedPaper.emit()
    if config.DEBUG:
      print("Emit userChangedPaper")
    # Persist
    self.pageSetup.toSettings()
    
    
  def _cancelSlot(self):
    '''
    PageSetupDialog or PrintDialog was canceled.
    
    No choices made by user are kept:
    - printerAdaptor still adapts same printer
    - pageSetup of adapted printer is unchanged.
    '''
    self.pageSetup.toControlView()  # restore view to equal unchanged model
    self.userCanceledPrintRelatedConversation.emit()
    if config.DEBUG:
      print("Emit userCanceledPrintRelatedConversation")
    
  
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
      print('>>>> Fixing invariant by setting paperSize on QPrinter', str(paper))
      # self.setPaperSize(paper.paperEnum)
      self.pageSetup.toPrinterAdaptor(printerAdaptor=self.printerAdaptor)
    if sys.platform.startswith('darwin'):
      paper = self.pageSetup.paper
      print('>>>> Darwin: always set paperSize on QPrinter', str(paper))
      # self.setPaperSize(paper.paperEnum)
      self.pageSetup.toPrinterAdaptor(printerAdaptor=self.printerAdaptor)


  '''
  Exported but delegated methods.
  To hide internal chains of delegation.
  '''
  @property
  def printablePageSize(self):
    return self.printerAdaptor.printablePageSize
  
  def paper(self):
    return self.printerAdaptor.paper()