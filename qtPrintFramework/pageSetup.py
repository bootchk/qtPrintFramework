

from PyQt5.QtCore import QObject, QSettings, QSizeF, QSize
from PyQt5.QtGui import QPagedPaintDevice  # !! Not in QtPrintSupport
from PyQt5.QtPrintSupport import QPrinter

from qtPrintFramework.paper.paper import Paper
from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.paper.custom import CustomPaper
from qtPrintFramework.orientedSize import OrientedSize
from qtPrintFramework.orientation import Orientation



class PageSetup(QObject):
  '''
  Persistent user's choice of page setup attributes.
  
  This defines the set of attributes.
  The editor (a dialog) defines the labels and models for attribute controls.
  Currently, we omit margins attribute of page setup.
  
  For a CustomPaper, we DO persist user's choice of size for the Custom paper.
  
  Responsibilities:
  - editable via a PageSetupDialog
    (user can also edit a 'the page setup" using a native dialog, but that comes here via PrinterAdaptor 
  - save/restore self to settings, so self persists with app, not with a printer
  - apply/get self to/from PrinterAdaptor (via native dialogs.)
  
  Almost a responsibility:
  - edit: a PageSetupDialog edits this, and knows this intimately by iterating over editable PageAttributes.
    But other dialogs (native) contribute to self state.
    See PrintRelatedConverser.
    Editor is also known as control/view.
  
  For some apps, a PageSetup (as a user choice) is an attribute of a document.
  For other apps, a PageSetup is only an attribute of a user (a setting.)
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
  
  def __init__(self, printerAdaptor, masterEditor):
    
    super(PageSetup, self).__init__()
    
    '''
    masterEditor is an editor whose model is the master, i.e. defined by Qt.
    All other editor model's are subsets.
    Self can be edited by many subclasses of editor i.e. RealPrinterPageSetupDialog and PrinterlessPageSetupDialog.
    I.E. editor is not constant and is passed for many methods.
    '''
    
    " Model.  Initialized to default from masterEditor's models."
    self.paper = StandardPaper(masterEditor.sizeControl.default())
    self.orientation = Orientation(masterEditor.orientationControl.default())
    
    " Possibly change default model from settings."
    self.initializeModelFromSettings(getDefaultsFromPrinterAdaptor=printerAdaptor)
    # Not assert that printerAdaptor equals self yet.
    
    '''
    Is is NOT an assertion that model equals editor.
    We only ensure that just before showing dialog
    ##self.toEditorExcludeCustom(masterEditor) # OR toEditor()
    ##assert self._isModelEqualEditor(masterEditor)
    '''
    
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
    self.paper = printerAdaptor.paper() # new instance
    self.orientation = printerAdaptor.paperOrientation
    if self.paper.isCustom:
      # capture size chosen by user, say in native Print dialog
      integralOrientedSizeMM = OrientedSize.roundedSize(sizeF=printerAdaptor.paperSizeMM)
      self.paper.setSize(integralOrientedSizeMM = integralOrientedSizeMM, 
                         orientation=self.orientation)
    # else size of paper is standard.
    
    # editor and settings are not updated                    
    
    
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
    
    printerAdaptor.setOrientation(self.orientation.value)
    
    # Formerly we called _toPrinterAdaptorByIntegralMMSize() here
    
    '''
    Set paper by enum where possible.  Why do we need this is additon to the above?
    Because floating point errors in some versions of Qt, 
    setting paperSize by a QSizeF does not always have the intended effect on enum.
    '''
    if self.paper.isCustom :
      # Illegal to call setPaperSize(QPrinter.Custom)
      self._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    else:
      printerAdaptor.setPaperSize(self.paper.paperEnum)
    
    '''
    Strong assertion might not hold: Qt might be showing paper dimensions QSizeF(0,0) for Custom
    (Which is bad programming.  None or Null should represent unknown.)
    
    Or, despite trying to set QPrinter consistent, Qt bugs still don't meet strong assertion.
    '''
    if not self.isEqualPrinterAdaptor(printerAdaptor):
      '''
      Setting by enum (non-custom) has failed.  (Typically on OSX?)
      Fallback: attempt to set by size.
      '''
      self._toPrinterAdaptorByIntegralMMSize(printerAdaptor)
    
    """
    Tried this for OSX, but it did not succeed in getting native dialog to agree with self.
    So Qt versions < 5.3 have a bug that cannot be worked around by this framework.
    if not self.isEqualPrinterAdaptor(printerAdaptor):
      self._toPrinterAdaptorByFloatInchSize(printerAdaptor)
    """
      
    if not self.isEqualPrinterAdaptor(printerAdaptor):
      '''
      Despite best efforts, could not get printerAdaptor (and the platform)
      to have page setup we desire.
      '''
      print(">>>>>>>>>>>>Warning: printerAdaptor pageSetup disagrees.")
      
      
    # Ideally (if Qt was bug free) these assertions should hold
    #assert self.isStronglyEqualPrinterAdaptor(printerAdaptor)
    #assert self.isEqualPrinterAdaptor(printerAdaptor)
    
  
  def _toPrinterAdaptorByIntegralMMSize(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Take integral size, convert to float.
    '''
    # Even a Custom paper has a size, even if it is defaulted.
    newPaperSizeMM = QSizeF(self.paper.integralOrientedSizeMM(self.orientation))
    assert newPaperSizeMM.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    printerAdaptor.setPaperSize(newPaperSizeMM, QPrinter.Millimeter)
    
    
  def _toPrinterAdaptorByFloatInchSize(self, printerAdaptor):
    '''
    Set my values on printerAdaptor (and whatever printer it is adapting) by setting size.
    
    Floating inch size.
    '''
    # TODO oriented, other inch unit sizes
    if self.paper.paperEnum == QPrinter.Legal:
      newPaperSizeInch = QSizeF(8.5, 14)
    elif self.paper.paperEnum == QPrinter.Letter:
      newPaperSizeInch = QSizeF(8.5, 11)
    else:
      return
      
    assert newPaperSizeInch.isValid()
    # use overload QPrinter.setPaperSize(QPagedPaintDevice.PageSize, Units)
    print("setPaperSize(Inch)", newPaperSizeInch)
    printerAdaptor.setPaperSize(newPaperSizeInch, QPrinter.Inch)
    
  
    
  '''
  To/from settings.
  
  Assert that QSettings have been established on client app startup:
  QCoreApplication.setOrganizationName("Foo")
  QCoreApplication.setOrganizationDomain("foo.com")
  QCoreApplication.setApplicationName("Bar")
  
  toSettings is called in reaction to dialog accept see PrintRelatedConverser.
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
    self.orientation = Orientation(self._intForSetting(orientationValue))
    
    size = QSize(self._intForSetting(integralOrientedWidthValue),
                self._intForSetting(integralOrientedHeightValue))
    self.paper = self._paperFromSettings(paperEnum=self._intForSetting(enumValue),
                                         integralOrientedPaperSize=size,
                                         orientation=self.orientation)
    qsettings.endGroup()
    assert isinstance(self.paper, Paper)  # !!! Might be custom of unknown size
    assert isinstance(self.orientation, Orientation)
    print("PageSetup from settings:", str(self))
  
  
  def toSettings(self):
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )
    # Although Paper is pickleable, simplify to int.  QSettings stores objects correctly?
    qsettings.setValue( "paperEnum", self.paper.paperEnum )
    qsettings.setValue( "paperOrientation", self.orientation.value )
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
  Model values to/from editors
  Exported to printRelatedConverser.
  View diverges from model while dialog is active.
  When dialog is accepted or canceled, view and model are made equal again.
  
  # TODO if printer has been removed since settings created, this may fail
  '''
  
  def toEditor(self, editor):
    # Allow Custom
    editor.sizeControl.setValue(self.paper.paperEnum)
    editor.orientationControl.setValue(self.orientation.value)
    assert self._isModelEqualEditor(editor)
    
    
  def toEditorExcludeCustom(self, editor):
    '''
    To view, except if self is Custom,
    select another default value in view.
    (Before displaying view, we will warn the user that the view
    does permit editing a Custom PageSetup.)
    '''
    if self.paper.paperEnum == QPrinter.Custom:
      # Not allow Custom into dialog
      editor.sizeControl.setValue(0) # Typically A4 ?
    else:
      editor.sizeControl.setValue(self.paper.paperEnum)
    editor.orientationControl.setValue(self.orientation.value)
    assert self._isModelEqualEditor(editor)


  """
  def restoreEditorToModel(self, editor):
    # canceled edit
    self.toEditorExcludeCustom(editor)
  """
    
  
  def fromEditor(self, editor):
    ''' 
    NonNative PageSetup Dialog was accepted.  Capture values from view to model.
    
    Dialog DOES allow choice of Custom, but not specifying size: will default.
    
    Since Dialog defaults size of Custom, Dialog cannot be used to just change
    the orientation of an existing Custom paper???
    '''
    # Orientation choice is meaningful even if paper is Custom with default size?
    self.orientation = Orientation(editor.orientationControl.value)
    
    # Create new instance of Paper from enum.  Old instance garbage collected.
    self.paper = self._paperFromEnum(editor.sizeControl.value)
    
    assert self._isModelEqualEditor(editor)
    
  
  '''
  Assertion support
  '''
  def _isModelEqualEditor(self, editor):
    # allow one disparity: self is Custom and view is A4.  See toEditor.
    result = ( self.paper.paperEnum == editor.sizeControl.value or self.paper.paperEnum == QPrinter.Custom and editor.sizeControl.value == 0) \
          and self.orientation.value == editor.orientationControl.value
    if not result:
      print(self.paper, self.orientation, editor.sizeControl.value, editor.orientationControl.value)
    return result
  
  def isEqualPrinterAdaptor(self, printerAdaptor):
    '''
    Weak comparison: computed printerAdaptor.paper() equal self.
    printerAdaptor.paperSize() might still not equal self.paperEnum
    '''
    result = self.paper == printerAdaptor.paper() and self.orientation == printerAdaptor.paperOrientation
    if not result:
      print("pageSetup differs:", 
            self.paper.orientedDescription(self.orientation), 
            printerAdaptor.paper().orientedDescription(printerAdaptor.paperOrientation))
    return result
  
  def isStronglyEqualPrinterAdaptor(self, printerAdaptor):
    '''
    Strong comparison: enum, orientation, dimensions equal
    
    Comparison of dimensions is epsilon (one is integer, one is float.
    Comparison of dimensions is unoriented (usually, width < height, but not always, Tabloid/Ledger).
    '''
    # partialResult: enums and orientation
    partialResult = self.paper.paperEnum == printerAdaptor.paperSize() \
          and self.orientation == printerAdaptor.paperOrientation
    
    # Compare sizes.  All Paper including Custom has a size.
    sizeResult = partialResult and self.paper.isOrientedSizeEpsilonEqual(self.orientation, printerAdaptor.paperSizeMM)
    
    result = partialResult and sizeResult
      
      
    if not result:
      print('isStronglyEqualPrinterAdaptor returns False')
      print(self.paper.paperEnum, printerAdaptor.paperSize(), # our and Qt enums
            self.orientation, printerAdaptor.orientation(), # our and Qt orientation
            printerAdaptor.paperSizeMM ) # Qt paperSize(mm)
      if not self.paper.isCustom:
        print (self.paper.integralOrientedSizeMM(self.orientation) )  # our size mm (not defined for Custom)
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
                           orientation=Orientation()) # default to Portrait
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

  