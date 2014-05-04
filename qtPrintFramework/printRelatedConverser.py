

from copy import copy

from PyQt5.QtCore import QObject
from PyQt5.QtPrintSupport import QPageSetupDialog, QPrintDialog

from PyQt5.QtCore import pyqtSignal as Signal

from qtPrintFramework.printerAdaptor import PrinterAdaptor
from qtPrintFramework.userInterface.dialog.printerlessPageSetup import PrinterlessPageSetupDialog
from qtPrintFramework.userInterface.dialog.realPrinterPageSetup import RealPrinterPageSetupDialog
from qtPrintFramework.userInterface.warn import Warn
from qtPrintFramework.pageSetup import PageSetup

import qtPrintFramework.config as config


class InvalidPageSize(Exception):
  pass



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
    self.warn = Warn(parentWidget)
    
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
    self.pageSetup = PageSetup(self.printerAdaptor, control=self.toFilePageSetupDialog)
    
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
    
    Dispatch to native or non-native dialog according to current printer.
    
    If you use this, you should retitle the non-native dialog to distinguish it from the native one.
    '''
    if self.printerAdaptor.isAdaptingNative():
      self._conversePageSetupNative()
    else:
      self.conversePageSetupNonNative()

    
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer, or in it's setup.)
    The conversation if accepted may include a change in self's state (user chose a different printer)
    AND a change in state of the adapted printer (user chose a different paper, etc.)
    
    On some platforms, user CAN choose different printer during page setup.
    '''
    
    
  def conversePrint(self):
    '''
    Start a print conversation, using native print dialog.
    
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
    
        
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer.)
    The conversation if accepted may include a change in self's state (user chose a different printer.)
    '''
  
  
  def conversePrintPDF(self):
    '''
    Start a print PDF conversation.
    
    Only necessary on Win, where native print dialog does not offer choice to print PDF.
    
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
    
  def conversePageSetupNonNative(self):
    '''
    Use framework's dialog (which is non-native, doesn't use native dialogs.)
    
    This MUST be used with non-native printers (Qt has no PageSetup dialog for non-native printers.)
    This CAN be used with native printers (thus it is exported from framework.)
    
    It omits many page features such as margins and custom paper dimensions.
    
    It will not set up a Custom paper.
    '''
    self.dump("NonNative page setup to")
    
    # Do we need this warning? User will learn soon enough?
    if self.pageSetup.paper.isCustom:
      self.warn.pageSetupNotUsableOnCustomPaper()
    
    # TODO isAdaptingReal ?
    if self.printerAdaptor.isAdaptingNative():
      '''
      native printer is real printer or to file printer
      Create new dialog having title and papersizemodel from printerAdaptor.
      '''
      dialog = RealPrinterPageSetupDialog(parentWidget=self.parentWidget, printerAdaptor=self.printerAdaptor)
    else:
      # Use static dialog having fixed title and paperSize model from Qt
      dialog = self.toFilePageSetupDialog
    
    self._showPrintRelatedDialogWindowModal(dialog, acceptSlot=self._acceptNonNativePageSetupSlot)
    # execution continues but conversation not complete
    
    
    
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
    dialog = QPageSetupDialog(self.printerAdaptor, parent=self.parentWidget)
    self._showPrintRelatedDialogWindowModal(dialog, acceptSlot=self._acceptNativePageSetupSlot)
    
    
  '''
  Print
  '''
    
  def _conversePrintNative(self):
    
    self.dump("Native print to")
    
    self.checkInvariantAndFix()
    self.printerAdaptor.ensureReadyForNativeDialog()
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
    try:
      _ = self.printablePageSize
      self.userAcceptedPrint.emit()
      if config.DEBUG:
        print("Emit userAcceptedPrint")
    except InvalidPageSize:
      self.warn.pageTooSmall()
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
    self.pageSetup.restoreViewToModel()
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
    
    """
    if sys.platform.startswith('darwin'):
      paper = self.pageSetup.paper
      print('>>>> Darwin: always set inch paperSize on QPrinter', str(paper))
      '''
      Not just toPrinterAdaptor(), since printerAdaptor may agree with pageSetup,
      (on enums, and float sizes to epsilon)
      but platform native dialog may disagree with printerAdaptor.
  
      Call _toPrinterAdaptorByFloatInchSize() which might be more effective.
      '''
      self.pageSetup._toPrinterAdaptorByFloatInchSize(self.printerAdaptor)
    """
    
    self.dump("After checkInvariantAndFix")


  '''
  Exported but delegated methods.
  To hide internal chains of delegation.
  '''
  @property
  def printablePageSize(self):
    '''
    QSizeF that is:
    - not empty (both w and h > 0)
    else InvalidPageSize.
    
    Units DevicePixel
    
    Assert not empty implies isValid, which is both w and h >= 0.
    
    Exported because app may wish to know page size even if not printing.
    '''
    result = self.printerAdaptor.printablePageSize
    if result.isEmpty():
      raise InvalidPageSize
    return result
  
  
  def paper(self):
    return self.printerAdaptor.paper()