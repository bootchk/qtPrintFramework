
from PyQt5.QtCore import QObject, QSizeF, pyqtSlot  # QSize, 
from PyQt5.QtCore import pyqtSignal as Signal

# !!! This does not depend on QtPrintSupport, but certain subclasses do

from qtPrintFramework.exceptions import InvalidPageSize
from qtPrintFramework.warn import Warn
from qtPrintFramework.alertLog import debugLog # alertLog, 



class Converser(QObject):
  '''
  Knows how to conduct conversations about printers:
  - print
  - page setup
  
  Knows parentWidget of dialogs.  Hides modality of dialogs.
  
  Knows attributes of printer and page setup: delegates.
  
  Hides non-native/native printer distinction: dispatches.
  
  Knows that a reference to dialogs must be kept so they are not destroyed prematurely (especially native).
  
  Implementation:
  owns a PageLayout and a PrinterAdaptor and Dialogs.
  An app owns only a PrintConverser (usually wrapped in a PrintSession, not included here.)
  
  !!! No circular references, otherwise you get segfaults on app quit when things are destroyed in wrong order.
  '''
  
  
  '''
  Meaning of signals:
  -------------------
  userChangedLayout: user changed attribute of layout (any of paper, orientation, ...).  May occur more than once per page stetup dialog
  
  userAcceptedFoo: user pushed OK button on a dialog
  
  userCanceledPrintRelatedConversation: user pushed Cancel button on dialog.  
     Deprecated: now dialogs cannot be canceled (changes are live and cannot be undone by canceling.)
     
  Algebra of signals:
  -------------------
  
  userChangedPrinter and userChangedLayout are emitted before other signals
  
  userChangedPrinter and userChangedLayout are NOT emitted unless there is a change 
  (not emitted if user is offered choice but OK's when choice is same as previous.)
  
  userChangedPrinter and userChangedLayout are NOT emitted if userCanceledPrintRelatedConversation is emitted
  
  userAcceptedFoo and userCanceledPrintRelatedConversation are mutually exclusive
  '''
  userChangedLayout = Signal(int)
  
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
    super().__init__()
    self.parentWidget = parentWidget
    self.warn = Warn(parentWidget)
    
    # !!! Keep reference to dialogs so they are not prematurely destroyed, especially OSX
    self.currentFrameworkPageSetupDialog = None  # which dialog instance (provided by framework) is in use.
    self.nativePrintDialog = None
    self.nativePageSetupDialog = None
    
    '''
    A Converser owns PageLayout: model.
    Call subclass to get specialized PageLayout and dialogs and other attributes (PrinterAdaptor.)
    This has side effects (affects self's attributes not passed as parameters): setting dialogs.
    '''
    self.pageLayout = self.getPageLayoutAndDialog(parentWidget)
   
    '''
    Layout changes whenever one of its component changes.
    Connect both component signals (reduce) to one signal out of the framework.
    Note the signals from components have a parameter: so must userChangedLayout
    '''
    #TODO self.userChangedLayout.connect(self.pageLayout.paper.paperChanged)
    self.pageLayout.orientation.valueChanged[int].connect(self.userChangedLayout[int])
    
    
    
  def dump(self, condition):
    debugLog(condition)
    # debugLog(self.printerAdaptor.description)


  def getPageLayoutAndDialog(self, parentWidget):
    raise NotImplementedError('Deferred')

  '''
  Exported print related conversations (dispatch according to native/nonnative.)
  '''
      
  def conversePageSetup(self):
    '''
    Start a Page Setup conversation
    
    Specialized by subclasses
    '''
    raise NotImplementedError('Deferred')

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
    Specialized by subclasses.
    '''
    raise NotImplementedError('Deferred')
        
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
    
    self.setCurrentFrameworkPageSetupDialog() # responsibility of subclass
    assert self.currentFrameworkPageSetupDialog is not None
    
    
    # Do we need this warning? User will learn soon enough?
    #OLD paper.isCustom isCompatibleWithEditor
    if not self.pageLayout.isCompatibleWithEditor(self.currentFrameworkPageSetupDialog):
      self.warn.pageSetupNotUsableOnCustomPaper()
      
    # Ensure editor value matches pageSetup, or is default
    self.pageLayout.toEditor(self.currentFrameworkPageSetupDialog)
      
    self._showPrintRelatedDialogWindowModal(dialog=self.currentFrameworkPageSetupDialog, 
                                            acceptSlot=self._acceptNonNativePageSetupSlot)
    # execution continues but conversation not complete
    
  
      
  '''
  Print
  '''
    
    
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
    
  
  @pyqtSlot()
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
    '''
    try:
      # Test validity of pagesize
      _ = self.printablePageSizeInch()
      self.userAcceptedPrint.emit()
      debugLog("Emit userAcceptedPrint")
    except InvalidPageSize:
      self.warn.pageTooSmall()
      '''
      Not emit, so that printing will not proceed!!
      Caller must NOT attempt print with current printerAdaptor and PageSetup,
      since printablePageSize not isValid() and will typically throw another exception e.g. for division by zero.
      '''
      
    # regardless of validity, choice goes to settings
    self.pageLayout.toSettings()
    

  @pyqtSlot()
  def _acceptNonNativePrintSlot(self):
    '''
    A nonnative PrintDialog was accepted.
    User does not have choices for printer, but by choosing this action, makes 'PDF' the current printer?
    User may have changed it's page setup.
    User may have chosen a new file.
    
    Whether native printer or non-native printer (user changed printer)
    reflect user's choices into PageSetup.
    '''
    """
    TODO
    If non-native print allows choice of PageSetup, we need something like:
    self._capturePageSetupChange()
    """
    self.dump("Accept non-native print dialog on")

    self.userAcceptedPrintPDF.emit()
    debugLog("Emit userAcceptedPrintPDF")

    self.pageLayout.toSettings()

    
  @pyqtSlot()
  def _acceptNonNativePageSetupSlot(self):
    '''
    User accepted NonNative PageSetupDialog.
    
    Dialog does not allow user to change adapted printer.
    User might have changed page setup,
    but they have not been applied to a PrinterAdaptor.
    
    !!! This is similar, but not the same as _capturePageSetupChange()
    Here, user made change in a non-native dialog that hasn't yet affected printerAdaptor
    '''
    self.dump("accept nonnative page setup, printerAdaptor before setting it")
    
    """
    OLD Formerly we optimized by checking that pageLayout had actually changed.
    And we did not propagate signals to userChangedLayout if nothing had changed.
    Now we connect paperChanged and orientationChanged to userChangedLayout
    oldPageSetup = copy(self.pageLayout)
    self.pageLayout.fromEditor(self.currentFrameworkPageSetupDialog)
    if not oldPageSetup == self.pageLayout:
      self._propagateChangedPageSetup()
      self._emitUserChangedPaper()
    """
    self._emitUserChangedLayout()
    
    self.dump("accept nonnative page setup, printerAdaptor after setting it")

    self.userAcceptedPageSetup.emit()
    debugLog("Emit userAcceptedPageSetup")
    
    self.pageLayout.toSettings()
    
    
  def __capturePageSetupChange(self):
    raise NotImplementedError('Deferred')
  
  def _propagateChangedPageSetup(self):
    '''
    Some subclasses actually propagate.
    TODO Why doesn't the signal suffice?  Because this is internal?
    '''
    raise NotImplementedError('Deferred')
  
    
  def _emitUserChangedLayout(self):
    '''
    User has chosen a new layout, either in Print or PageSetup dialog.
    '''
    # Tell the app
    self.userChangedLayout.emit(0)  # Unused arg to signal
    debugLog("Emit userChangedLayout")
    # Persist
    self.pageLayout.toSettings()


  @pyqtSlot()
  def _cancelSlot(self):
    '''
    PageSetupDialog or PrintDialog was canceled.
    
    No choices made by user are kept:
    - printerAdaptor still adapts same printer
    - pageSetup of adapted printer is unchanged.
    
    Editor's controls may have different values than the model.
    Must sync editor with model before using editor again.
    ##self.pageLayout.restoreEditorToModel()
    '''
    self.userCanceledPrintRelatedConversation.emit()
    debugLog("Emit userCanceledPrintRelatedConversation")
      
    # NOT self.pageLayout.toSettings()
    

  '''
  Exported but delegated methods.
  To hide internal chains of delegation.
  
  OBSOLETE in Qt: pageRect() which return DevicePixels
  '''
  
  def printablePageSizeInch(self):
    '''
    QSizeF that is:
    - not empty (both w and h > 0)
    else InvalidPageSize.
    
    Units Inch
    
    Assert not empty implies isValid, which is both w and h >= 0.
    
    Exported because app may wish to know page size even if not printing.
    '''
    raise NotImplementedError('Deferred')
    
    
  def _checkPrintablePageSizeInch(self, result):
    if result.isEmpty():
      raise InvalidPageSize
    assert isinstance(result, QSizeF)

  
  def paper(self):
    '''
    Paper chosen by user.
    '''
    raise NotImplementedError('Deferred')
  
  