

from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport

from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.paper.custom import CustomPaper
from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.paperSize import PaperSizeModel # singleton
from qtPrintFramework.model.pageOrientation import PageOrientationModel # singleton


class PageSetup(list):
  '''
  Persistent user's choice of page setup.
  
  Iterable container of attributes of a page.
  
  This defines the set of attributes, their labels and models.
  
  Responsibilities:
  - iterate PageAttributes (which are editable)
  - save/restore self to settings, so self persists with app, not with a printer
  - apply/get self to/from PrinterAdaptor
  
  Almost a responsibility:
  - edit: PrinterlessPageSetupDialog edits this, and knows this intimately by iterating over editable PageAttributes.
    But other dialogs (native) contribute to self state.
    See PrintRelatedConverser.
  
  !!! Paper/Page are not interchangeable but refer to a similar concept.
  Paper connotes real thing, and Page an ideal concept.
  They are often both confusingly used for the ideal concept (regardless of whether real thing is involved.)
  '''
  
  def __init__(self, printerAdaptor):
    
    " Model "
    self.paper = StandardPaper(PaperSizeModel.default())
    self.orientation = PageOrientationModel.default()
    
    " Control/views"
    self.append(PageAttribute(label="Size", model=PaperSizeModel))
    self.append(PageAttribute(label="Orientation", model=PageOrientationModel)) # ('Portrait', 'Landscape')))
    
    " Possibly change default model from settings."
    self.initializeModelFromSettings(printerAdaptor)
    
    " Ensure model equals view"
    self.toControlView()
    assert self.isModelEqualView()
    
    '''
    It is NOT an assertion that self.isEqualPrinterAdaptor(printerAdaptor)
    in the case that printerAdaptor is adapting a native printer.
    That is, we don't force a native printer's page setup onto self (on user's preferred pageSetup for document),
    until user actually chooses to print on said native printer.
    '''

  
  def __eq__(self, other):
    return self.paper == other.paper and self.orientation == other.orientation
  

  def initializeModelFromSettings(self, printerAdaptor):
    '''
    If current printer is NonNative, self's settings pertain to it.
    (a NonNative printer by definition does not own a persistent page setup,
    i.e. the platform doesn't necessarily know of the printer, let alone know its page setup.
    The app persists a PageSetup for such printers.)
    
    Otherwise, user has used another real printer since
    this app was last used, and that printer's persistent PageSetup
    will show in it's native dialogs, 
    and will be captured to self after those dialogs are used.
    '''
    if not printerAdaptor.isAdaptingNative():
      self.fromSettings()
    
    
    
  '''
  To/from printerAdaptor
  
  Alternative design: illustrates general nature.
    for attribute in self:
      attribute.toPrinterAdaptor(printerAdaptor)
  '''

  def fromPrinterAdaptor(self, printerAdaptor):
    '''
    Copy values from printerAdaptor into self.
    And update controls (which are not visible, and are in parallel with native dialog controls.)
    '''
    self.paper = printerAdaptor.paper()
    self.orientation = printerAdaptor.orientation()
    self.toControlView()
    self.toSettings()   # TODO optimization: only if non-native
    
    
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting.)
    '''
    '''
    1. !!! setPaperSize,  setPageSize() is Qt obsolete
    2. printerAdaptor wants oriented size
    '''
    '''
    !!! setPaperSize is overloaded.
    # TODO should this be orientedPaperSizeDevicePixels ?
    '''
    """
    TODO printerAdaptor wants oriented size????
    if self.paper.pageSize == Custom:
      
    else:
      printerAdaptor.setPaperSize(self.paper.orientedSizeMM(self.orientation), QPrinter.Millimeters)
    """
    printerAdaptor.setPaperSize(self.paper.paperSize) # !!! Enum only
    printerAdaptor.setOrientation(self.orientation)
    
    
  '''
  To/from settings.
  
  Assert that QSettings have been established on client app startup:
  QCoreApplication.setOrganizationName("Foo")
  QCoreApplication.setOrganizationDomain("foo.com")
  QCoreApplication.setApplicationName("Bar")
  '''
    
  def fromSettings(self):
    '''
    Set my values from settings (that persist across app sessions.)
    If settings don't exist yet, use default value from model.
    '''
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    self.paper = qsettings.value( "paper", PaperSizeModel.default())
    self.orientation = qsettings.value( "paperOrientation", PageOrientationModel.default())
    qsettings.endGroup()
  
  def toSettings(self):
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    qsettings.setValue( "paper", self.paper )   # just .paperSize ?
    qsettings.setValue( "paperOrientation", self.orientation )
    qsettings.endGroup()
  
  
  '''
  Model values to/from control/views
  Exported to printRelatedConverser.
  View diverges from model while dialog is active.
  When dialog is accepted or canceled, view and model are made equal again.
  '''
  def toControlView(self):
    self[0].setValue(self.paper.paperSize)
    self[1].setValue(self.orientation)
    assert self.isModelEqualView()
    
  def fromControlView(self):
    ''' 
    Dialog was accepted.  Capture values from view to model.
    '''
    # Create new instance of Paper from enum.  Old instance garbage collected.
    pageSize = self[0].value
    if pageSize == QPagedPaintDevice.Custom:
      self.paper = CustomPaper()
    else:
      self.paper = StandardPaper(pageSize)
      
    # TODO meaningless choice if paper is Custom with unknown size?
    self.orientation = self[1].value
    assert self.isModelEqualView()
    
  
  '''
  Assertion support
  '''
  def isModelEqualView(self):
    return self.paper.paperSize == self[0].value and self.orientation == self[1].value
  
  def isEqualPrinterAdaptor(self, printerAdaptor):
    result = self.paper == printerAdaptor.paper() and self.orientation == printerAdaptor.orientation()
    if not result:
      print(self.paper, printerAdaptor.paper())
    return result
  
  
  def dump(self):
    '''
    '''
    print(self.paper, self.orientation)

  