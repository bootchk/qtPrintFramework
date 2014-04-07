'''
'''
from PyQt5.QtCore import QSize
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.paper import Paper
from qtPrintFramework.printRelatedConverser import PrintConverser



class PrinterAdaptor(QPrinter):
  '''
  A thin wrapper around QPrinter hiding native distinction.
  
  QPrinter is itself an adaptor/controller: it adapts physical and virtual (e.g. to PDF file) printers.
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
  
  
  
  def doPageSetup(self):
    if self.isAdaptingNative():
      self.printConverser.doPageSetupNative(printerAdaptor=self)
    else:
      self.printConverser.doPageSetupNonNative(printerAdaptor=self)
    self.describePrinter()
    
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer, or in it's setup.)
    The conversation if accepted may include a change in self's state (user chose a different printer)
    AND a change in state of the adapted printer (user chose a different paper, etc.)
    
    TODO on any platforms, can user choose different printer during page setup?
    '''
    
    
  def doPrint(self):
    '''
    Do a print conversation.
    
    This understands differences by platform.
    '''
    if self.isAdaptingNative():
      self.printConverser.doPrintNative(printerAdaptor=self)
    else:
      if True:
        self.printConverser.doPrintNative(printerAdaptor=self)
      else:
        self.printConverser.doPrintNonNative(printerAdaptor=self)
        
    '''
    Execution continues, but conversation might be ongoing (if window modal or modeless)
    
    Conversation might be canceled and self's state unchanged (no change in adapted printer.)
    The conversation if accepted may include a change in self's state (user chose a different printer.)
    '''
  
  
  def describePrinter(self):
    '''
    Description of adapted printer.
    '''
    print("Printer name: ", self.printerName())
    print("   isNative", self.isAdaptingNative())
    print("   paper size:", self.paperSize() )  # Calls QPrinter, this is wrong in Qt < 5.3
    print("   paper:", self.paper())
    
  
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
  
  
  
    
    
    