

from PyQt5.QtCore import QSettings, QSizeF, QSize
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.paper.paper import Paper
from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.paper.custom import CustomPaper
from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.paperSize import PaperSizeModel # singleton
from qtPrintFramework.model.pageOrientation import PageOrientationModel # singleton
from qtPrintFramework.orientedSize import OrientedSize



class PageSetup(list):
  '''
  Persistent user's choice of page setup.
  
  Iterable container of attributes of a page.
  
  This defines the set of attributes, their labels and models.
  Currently, we omit margins attribute of page setup.
  
  For a CustomPaper, we DO persist user's choice of size for the Custom paper.
  
  Responsibilities:
  - iterate PageAttributes (which are editable)
  - save/restore self to settings, so self persists with app, not with a printer
  - apply/get self to/from PrinterAdaptor
  
  Almost a responsibility:
  - edit: PrinterlessPageSetupDialog edits this, and knows this intimately by iterating over editable PageAttributes.
    But other dialogs (native) contribute to self state.
    See PrintRelatedConverser.
  
  For some apps, a PageSetup (as a user choice) is an attribute of a document.
  For other apps, a PageSetup is only an attribute ofif orientation == a user (a setting.)
  Here, we always get it as a setting.
  If your app treats a PageSetup as a document attribute,
  you must call toPrinterAdaptor() (but it may not take.)
  
  !!! A PageSetup can be impressed on a PrinterAdaptor, but a PrinterAdaptor does not own one.
  A PrintConverser owns a PageSetup.
  An adapted printer (that a PrinterAdaptor adapts) might own a different object (which is opaque to us)
  that holds its notion of page setup.
  
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
    self.initializeModelFromSettings(getDefaultsFromPrinterAdaptor=printerAdaptor)
    # Not assert that printerAdaptor equals self yet.
    
    " Ensure model equals view"
    self.toControlView()
    assert self.isModelEqualView()
    
    '''
    It is NOT an assertion that self.isEqualPrinterAdaptor(printerAdaptor)
    in the case that printerAdaptor is adapting a native printer.
    That is, we don't force a native printer's page setup onto self (on user's preferred pageSetup for document),
    until user actually chooses to print on said native printer.
    '''


  def __repr__(self):
    '''
    Not strict: result will not recreate object.
    
    paperName orientationName orientedDimensions
    e.g. 'A4 Landscape 297x219mm'
    e.g. 'Custom Portrait 640x480mm'
    '''
    ## return ','.join((str(self.paper), str(self.orientation)))
    return self.paper.orientedDescription(self.orientation)
    ##return " ".joint((self.paper.name, self._orientationName(self.orientation)), self.paper)
    
  
  def __eq__(self, other):
    return self.paper == other.paper and self.orientation == other.orientation
  

  '''
  A NonNative printer by definition does not own a persistent page setup,
  i.e. the platform doesn't necessarily know of the printer, let alone know its page setup.
  The app persists a PageSetup for such printers.)
  
  A user might have used another real or native paperless printer since this app was last used.
  This PageSetup (and its persistent value)
  should be tryImpressed on adatped printer before it's dialogs are shown.
  Otherwise, the dialogs may show persistent (persisted by the platform) page setup
  of the adapted printer, or some other page setup.
  After user accepts such a dialog, we capture its page setup to self.
  '''
  def initializeModelFromSettings(self, getDefaultsFromPrinterAdaptor):
    #if not printerAdaptor.isAdaptingNative():
    self.fromSettings(getDefaultsFromPrinterAdaptor=getDefaultsFromPrinterAdaptor)
    
    
    
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
    if self.paper.isCustom:
      # capture size chosen by user, say in native Print dialog
      integralOrientedSizeMM = OrientedSize.roundedSize(sizeF=printerAdaptor.paperSizeMM)
      self.paper.setSize(integralOrientedSizeMM = integralOrientedSizeMM, 
                         orientation=self.orientation)
    # else size of paper is standard.
                          
    self.toControlView()
    self.toSettings()   # FUTURE optimization: only if non-native
    
    
  def toPrinterAdaptor(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting.)
    
    1. !!! setPaperSize,  setPageSize() is Qt obsolete
    2. printerAdaptor wants oriented size
    
    !!! setPaperSize is overloaded.
    # TODO should this be orientedPaperSizeDevicePixels ?
    
    Qt docs for setPaperSize() say: "Sets the printer paper size to newPaperSize if that size is supported. 
    The result is undefined if newPaperSize is not supported."
    The same applies here; this may not have the intended effect.
    '''
    
    printerAdaptor.setOrientation(self.orientation)
    
    # Even a Custom paper has a size, even if it is defaulted.
    newPaperSizeMM = QSizeF(self.paper.integralOrientedSizeMM(self.orientation))
    assert newPaperSizeMM.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize)
    printerAdaptor.setPaperSize(newPaperSizeMM, QPrinter.Millimeter)
    
    '''
    Also set paper by enum.  Why do we need this is additon to the above?
    Because floating point errors in some versions of Qt, 
    setting paperSize by a QSizeF does not always have the intended effect on enum.
    '''
    if self.paper.isCustom :
      # Illegal to call setPaperSize(QPrinter.Custom), but the above has intended effect
      pass
    else:
      printerAdaptor.setPaperSize(self.paper.paperEnum)
    
    '''
    TODO Strong assertion might not hold: Qt might be showing paper dimensions QSizeF(0,0) for Custom
    (Which is bad programming.  None or Null should represent unknown.)
    
    Or, despite trying to set QPrinter consistent, Qt bugs still don't meet strong assertion.
    '''
    #assert self.isStronglyEqualPrinterAdaptor(printerAdaptor)
    assert self.isEqualPrinterAdaptor(printerAdaptor)
    
    
  '''
  To/from settings.
  
  Assert that QSettings have been established on client app startup:
  QCoreApplication.setOrganizationName("Foo")
  QCoreApplication.setOrganizationDomain("foo.com")
  QCoreApplication.setApplicationName("Bar")
  '''
  
  def fromSettings(self, getDefaultsFromPrinterAdaptor):
    '''
    Set my values from settings (that persist across app sessions.)
    If settings don't exist yet, use default value from printerAdaptor
    Formerly, from model: PaperSizeModel.default(), PageOrientationModel.default()
    '''
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    
    enumValue = qsettings.value( "paperEnum", getDefaultsFromPrinterAdaptor.paper().paperEnum)
    orientationValue = qsettings.value( "paperOrientation", getDefaultsFromPrinterAdaptor.orientation() )
    defaultSize = CustomPaper.defaultSize()
    integralOrientedWidthValue = qsettings.value( "paperintegralOrientedWidth", defaultSize.width())
    integralOrientedHeightValue = qsettings.value( "paperintegralOrientedHeight", defaultSize.height())
    
    # Orientation first, needed for orienting paper size
    self.orientation = self._intForSetting(orientationValue)
    
    size = QSize(self._intForSetting(integralOrientedWidthValue),
                self._intForSetting(integralOrientedHeightValue))
    self.paper = self._paperFromSettings(paperEnum=self._intForSetting(enumValue),
                                         integralOrientedPaperSize=size,
                                         orientation=self.orientation)
    qsettings.endGroup()
    assert isinstance(self.paper, Paper)  # !!! Might be custom of unknown size
    assert isinstance(self.orientation, int)
    print("PageSetup from settings:", str(self))
  
  
  def toSettings(self):
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    # Although Paper is pickleable, simplify to int.  QSettings stores objects correctly?
    qsettings.setValue( "paperEnum", self.paper.paperEnum )
    qsettings.setValue( "paperOrientation", self.orientation )
    integralOrientedSize = self.paper.integralOrientedSizeMM(self.orientation)
    qsettings.setValue( "paperintegralOrientedWidth", integralOrientedSize.width())
    qsettings.setValue( "paperintegralOrientedHeight", integralOrientedSize.height())
    qsettings.endGroup()
  
  def _intForSetting(self, value):
    '''
    Ensure a settings value is type int, or 0 if can't convert.
    Settings values are unicode in PyQt.
    '''
    try:
      result = int(value)
    except ValueError:
      result = 0
    return result
  
  
  '''
  Model values to/from control/views
  Exported to printRelatedConverser.
  View diverges from model while dialog is active.
  When dialog is accepted or canceled, view and model are made equal again.
  '''
  def toControlView(self):
    """
    if self.paper.paperEnum == QPrinter.Custom:
      # Not allow Custom into dialog
      self[0].setValue(0)
    else:
      self[0].setValue(self.paper.paperEnum)
    """
    # Allow Custom
    self[0].setValue(self.paper.paperEnum)
    self[1].setValue(self.orientation)
    assert self.isModelEqualView()
    
  
  def fromControlView(self):
    ''' 
    NonNative PageSetup Dialog was accepted.  Capture values from view to model.
    
    Dialog DOES allow choice of Custom, but not specifying size: will default.
    
    Since Dialog defaults size of Custom, Dialog cannot be used to just change
    the orientation of an existing Custom paper???
    '''
    # Orientation choice is meaningful even if paper is Custom with default size?
    self.orientation = self[1].value
    
    # Create new instance of Paper from enum.  Old instance garbage collected.
    self.paper = self._paperFromEnum(self[0].value)
    
    assert self.isModelEqualView()
    
  
  '''
  Assertion support
  '''
  def isModelEqualView(self):
    # allow one disparity: self is Custom and view is A4.  See toControlView.
    result = ( self.paper.paperEnum == self[0].value or self.paper.paperEnum == QPrinter.Custom and self[0].value == 0) \
          and self.orientation == self[1].value
    if not result:
      print(self.paper, self.orientation, self[0].value, self[1].value)
    return result
  
  def isEqualPrinterAdaptor(self, printerAdaptor):
    '''
    Weak comparison: computed printerAdaptor.paper() equal self.
    printerAdaptor.paperSize() might still not equal self.paperEnum
    '''
    result = self.paper == printerAdaptor.paper() and self.orientation == printerAdaptor.orientation()
    if not result:
      print(self.paper, printerAdaptor.paper())
    return result
  
  def isStronglyEqualPrinterAdaptor(self, printerAdaptor):
    '''
    Strong comparison: enum, orientation, dimensions equal
    
    Comparison of dimensions is epsilon (one is integer, one is float.
    Comparison of dimensions is unoriented (usually, width < height, but not always, Tabloid/Ledger).
    '''
    # partialResult: enums and orientation
    partialResult = self.paper.paperEnum == printerAdaptor.paperSize() \
          and self.orientation == printerAdaptor.orientation()
    
    # Compare sizes.  All Paper including Custom has a size.
    sizeResult = partialResult and self.paper.isOrientedSizeEpsilonEqual(self.orientation, printerAdaptor.paperSizeMM)
    
    result = partialResult and sizeResult
      
      
    if not result:
      print('isStronglyEqualPrinterAdaptor returns False')
      print(self.paper.paperEnum, printerAdaptor.paperSize(), # our and Qt enums
            self.orientation, printerAdaptor.orientation(), # our and Qt orientation
            printerAdaptor.paperSizeMM ) # Qt paperSize(mm)
      if not self.paper.isCustom:
        print (self.paper.orientedSizeMM(self.orientation) )  # our size mm (not defined for Custom)
    return result
    
  
  def _paperFromEnum(self, paperEnum):
    '''
    Instance of a subclass of Paper for paperEnum.
    
    If Custom, default size.
    '''
    assert isinstance(paperEnum, int), str(type(paperEnum))
    if paperEnum == QPagedPaintDevice.Custom:
      # TODO warning dialog here
      print(">>>> Warning: PageSetup sets Custom paper to default size.  You may change size when you Print. ")
      result = CustomPaper(integralOrientedSizeMM=CustomPaper.defaultSize(),
                           orientation=QPrinter.Portrait)
    else:
      result = StandardPaper(paperEnum)
    return result
    
    
  def _paperFromSettings(self, paperEnum, integralOrientedPaperSize, orientation ):
    '''
    Instance of a subclass of Paper for settings values
    
    If Custom, size from settings.
    Otherwise, size defined for enum.
    '''
    assert isinstance(paperEnum, int), str(type(paperEnum))
    if paperEnum == QPagedPaintDevice.Custom:
      result = CustomPaper(integralOrientedSizeMM=integralOrientedPaperSize, 
                           orientation=orientation)
    else:
      result = StandardPaper(paperEnum)
    return result
    
    
    
  def dump(self):
    '''
    '''
    print(self.paper, self.orientation)

  