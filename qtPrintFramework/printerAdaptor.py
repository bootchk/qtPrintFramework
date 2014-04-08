



from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.paper import Paper
from qtPrintFramework.printRelatedConverser import PrintConverser



class PrinterAdaptor(QPrinter):
  '''
  A thin wrapper around QPrinter:
  - hides Qt's native/nonnative printer distinction
  - adds print PDF for platforms that don't support it (Win).  Linux already supports via Qt or and OSC natively.
  - fixes QTBUG TODO
  
  QPrinter is itself an adaptor/controller: it adapts physical and virtual (e.g. to PDF file) printers.
  
  Responsibilities:
  - hold conversations (dialogs, user interactions) related to printing (Print, PageSetup)
  - know which paper user has chosen
  - know printable rect (taking into account paper, margins, and paper orientation)
  - know user's choice of file (for paperless print)
  - emit signals when user accepts/cancels
  - emit signals when user chooses a different paper
  '''
  
  
  def __init__(self, parentWidget):
    super(PrinterAdaptor, self).__init__()
    self.printConverser = PrintConverser(parentWidget=parentWidget, printerAdaptor=self)
    
    
  def isAdaptingNative(self):
    '''
    is the current adapted printer a native printer (driver) ?
    
    Note that QPrinter has state: the printer it is adapting, which can change.
    
    isAdaptingNative() == True:  all Qt dialogs (which may call native dialogs) work with self.
    A native dialog is implemented by the platform, not Qt.
    
    not isAdaptingNative(): the adapted printer is implemented by Qt
    and the page setup dialog is implemented by qtPrintFramework.
    
    Currently, Qt PDF file printer driver is the only non-native one.
    
    The Qt PDF file printer:
    - not necessary on OSX since OSX natively offers print to PDF
    - necessary on Win if you need that capability, but it cannot be integrated with the native Win Print dialog
    - is seamlessly used on Linux by Qt (it visible in the Qt Print dialog.)
    
    In other words, if you pass a non-native printer:
          QPrintDialog  QPageSetupDialog
    Win:   fails          fails
    OSX:   
    Linux: works          fails
    
    '''
    return not self.outputFormat() == QPrinter.PdfFormat
  
  
  
  def conversePageSetup(self):
    '''
    Start a Page Setup conversation
    '''
    if self.isAdaptingNative():
      self.printConverser.conversePageSetupNative(printerAdaptor=self)
    else:
      self.printConverser.conversePageSetupNonNative(printerAdaptor=self)

    
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer, or in it's setup.)
    The conversation if accepted may include a change in self's state (user chose a different printer)
    AND a change in state of the adapted printer (user chose a different paper, etc.)
    
    TODO on any platforms, can user choose different printer during page setup?
    '''
    
    
  def conversePrint(self):
    '''
    Start a print conversation.
    
    This understands differences by platform.
    '''
    if self.isAdaptingNative():
      self.printConverser.conversePrintNative(printerAdaptor=self)
    else:
      if True:
        self.printConverser.conversePrintNative(printerAdaptor=self)
      else:
        self.printConverser.conversePrintNonNative(printerAdaptor=self)
        
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
    self.printConverser.conversePrintNonNative(printerAdaptor=self)
  
  
  @property
  def description(self):
    '''
    Description of adapted printer.
    '''
    # self.paperSize() calls QPrinter, wrong in Qt < 5.3
    terms = ( "Name", self.printerName(),
              "isNative", str(self.isAdaptingNative()),
              "paper size enum from Qt", str(self.paperSize()),
              "paper from qtPrintFramework", str(self.paper()) )
    return ','.join(terms)
  
  
  def paper(self):
    '''
    User's choice of paper.
    
    !!! Ameliorates a bug in Qt, whereby a QPrinter.paperSize() returns value that does not match pageSize().
    e.g. Returns Custom, dimensions of Letter when in fact user chose 'Letter'
    
    Also, returns a more capable object than QPrinter.paperSize(), which is only an enum value (a feeble subclass of int.)
    '''
    
    '''
    fix Qt bug.
    Create a Paper object by calling class method of Paper that returns proper enum that matches my floating page dimensions
    Using a dialog on QPrinter returns paperSize that is floating but not stable across platforms and doesn't compare exactly to integral Paper
    '''
    
    # !!! Not call deprecated pageSize(), it is in error also.
    # The overloaded paperSize(MM) returns an epsilon correct (except for floating precision) correct result
    floatPaperDimensionsMM = self.paperSize(QPrinter.Millimeter)
    correctPaperEnum = Paper.fuzzyMatchPageSize(floatPaperDimensionsMM)
    if correctPaperEnum is None:
      # self's pageSize doesn't match any standard Paper, it must be Custom
      # Which should be what self's paperSize() is saying
      assert False  
      # TODO
      # self.paperSize() == .Custom
      #result = CustomPaper()
    else:
      result = Paper(correctPaperEnum)  # TODO StandardPaper
    assert isinstance(result, Paper)
    return result
  
  
  
    
    
    