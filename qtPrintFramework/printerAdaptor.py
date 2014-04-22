

from PyQt5.QtCore import QSize
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.paper.paper import Paper
from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.paper.custom import CustomPaper



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
    - is partially used on Linux by Qt (is visible in Qt Print dialog but QPageSetupDialog fails.)
    
    In other words, if you pass a non-native QPrinter (outputFormat == PDF):
          QPrintDialog  QPageSetupDialog
    OSX:   fail          fail
    Win:   fail          fail
    Linux: work          fail
    
    '''
    return not self.outputFormat() == QPrinter.PdfFormat
  

    
  
  @property
  def description(self):
    '''
    Description of adapted printer.
    '''
    # self.paperSize() calls QPrinter.paperSize(), wrong in Qt < 5.3 returns Custom when it shouldn't
    terms = ( "Name:" + self.printerName(),
              "isNative:"+ str(self.isAdaptingNative()),
              "Qt paper enum:"+ str(self.paperSize()),
              # "qtPFramework setup:"+ str(self.printConverser.pageSetup),
              # "printable rect:"+ str(self.printablePageRect()),
              "paper size MM:"+ str(self.paperSizeMM),
              "paper size Inch:"+ str(self.paperSize(QPrinter.Inch)),
              "paper size DP:"+ str(self.paperSize(QPrinter.DevicePixel)),
              "print rect MM:" + str(self.pageRect(QPrinter.Millimeter)),
              "orientation:" + str(self.orientation()))
    return '\n   '.join(terms)
  
  
  
  
  def paper(self):
    '''
    New Paper instance representing user's choice of paper.
    
    !!! Ameliorates a bug in Qt, whereby a QPrinter.paperSize() returns value that does not match dimensions i.e. paperSize(Millimeter).
    e.g. paperSize() returns Custom, paperSize(Millimeter) dimensions of Letter when in fact user chose 'Letter'
    
    Also, returns a more capable object than QPrinter.paperSize(), which is only an enum value (a feeble subclass of int.)
    '''
    
    '''
    fix Qt bug.
    Create a Paper object by calling class method of Paper that returns proper enum that matches my floating page dimensions
    Using a dialog on QPrinter returns paperSize that is floating but not stable across platforms and doesn't compare exactly to integral Paper
    '''
    
    # !!! Not call deprecated self.pageSize(), it is in error also.
    # The overloaded paperSize(MM) returns an epsilon correct (except for floating precision) correct result
    floatPaperDimensionsMM = self.paperSizeMM
    correctPaperEnum = Paper.enumForPageSizeByMatchDimensions(floatPaperDimensionsMM)
    if correctPaperEnum is None:
      # self's paperSize(Millimeter) doesn't match any StandardPaper therefore self.paperSize() should be Custom
      assert self.paperSize() == QPagedPaintDevice.Custom
      size = OrientedSize.roundedSize(floatPaperDimensionsMM)
      if size is None:
        # Rounding failed: Qt passed a long
        # TODO Better to set to some non-zero default, or to emulate Qt's large size?
        print("Rounding failed, setting CustomPaper to default size.")
        result = CustomPaper(CustomPaper.defaultSize(), orientation=self.orientation)
      else:
        result = CustomPaper(integralOrientedSizeMM=size, orientation=self.orientation())
    else:
      result = StandardPaper(correctPaperEnum)  
    assert isinstance(result, (StandardPaper, CustomPaper))
    '''
    !!! result.paperEnum might not agree with self.paperSize() because of the Qt bug.
    '''
    return result
  
  
  
  '''
  Methods that alias Qt methods for clarification
  
  orientation() is not aliased
  '''
      
  def printablePageRect(self):
    '''
    Rect that can be printed. Paper less printer's limitations (unprintable) less user defined margins.
    
    Units DevicePixel
    '''
    '''
    If paper is Custom, data is flowing not from a defined paper,
    but from user using platform native dialog through printerAdaptor,
    or in some cases, a default size (this framework punts.)
    Qt may be punting in other situations.
    '''
    return self.pageRect()  # Delegate to QPrinter
  
  @property
  def printablePageSize(self):
    '''
    QSize of printable rect.  Units DevicePixel
    '''
    result = self.printablePageRect().size()
    assert isinstance(result, QSize)
    # !!! not ensuring it isValid() and not isEmpty()
    return result
  
  
  @property
  def paperSizeMM(self):
    '''
    QSizeF of oriented paper (usually larger than printablePageRect.)
    Units mm.
    Implementation: call an overloaded QPrinter method.
    '''
    return self.paperSize(QPrinter.Millimeter)
    
    
    