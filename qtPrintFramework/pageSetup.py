

from PyQt5.QtCore import QSettings

from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.paperSize import PaperSizeModel # singleton
from qtPrintFramework.model.pageOrientation import PageOrientationModel # singleton


class PageSetup(list):
  '''
  Iterable container of attributes of a page.
  
  This defines the set of attributes, their labels and models.
  
  Responsibilities:
  - iterate PageAttributes (which know their labels, controls, models, and values (but values are view values.)
  - save/restore self to settings, so self persists with app, not with a printer TODO
  - apply/get self to/from PrinterAdaptor
  
  !!! Paper/Page are not interchangeable but refer to a similar concept.
  Paper connotes real thing, and Page an ideal concept.
  They are often both confusingly used for the ideal concept (regardless of whether real thing is involved.)
  '''
  
  def __init__(self, printerAdaptor):
    
    " Model "
    self.paperSize = PaperSizeModel.default()
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
    '''


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
    self.paperSize = printerAdaptor.paperSize()
    self.orientation = printerAdaptor.orientation()
    self.toControlView()
    self.toSettings()   # TODO optimization: only if non-native
    
    
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting.)
    '''
    printerAdaptor.setPaperSize(self.paperSize)   # !!! PaperSize,  setPageSize() is Qt obsolete
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
    self.paperSize = qsettings.value( "paperSize", PaperSizeModel.default())
    self.orientation = qsettings.value( "paperOrientation", PageOrientationModel.default())
    qsettings.endGroup()
  
  def toSettings(self):
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    qsettings.setValue( "paperSize", self.paperSize )
    qsettings.setValue( "paperOrientation", self.orientation )
    qsettings.endGroup()
  
  
  '''
  Model values to/from control/views
  Exported to printRelatedConverser.
  View diverges from model while dialog is active.
  When dialog is accepted or canceled, view and model are made equal again.
  '''
  def toControlView(self):
    self[0].setValue(self.paperSize)
    self[1].setValue(self.orientation)
    assert self.isModelEqualView()
    
  def fromControlView(self):
    ''' 
    Dialog was accepted.  Capture values. 
    '''
    self.paperSize = self[0].value
    self.orientation = self[1].value
    assert self.isModelEqualView()
    
  
  '''
  Assertion support
  '''
  def isModelEqualView(self):
    return self.paperSize == self[0].value and self.orientation == self[1].value
  
  def isEqualPrinterAdaptor(self, printerAdaptor):
    return self.paperSize == printerAdaptor.paperSize() and self.orientation == printerAdaptor.orientation()
  
  
  def dump(self):
    '''
    Dump values.
    Note values are from the control/view,
    '''
    for attribute in self:
      print attribute.value
  