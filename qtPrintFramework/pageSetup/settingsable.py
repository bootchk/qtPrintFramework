
from PyQt5.QtCore import QSettings, QSize
from PyQt5.QtGui import QPagedPaintDevice

from qtPrintFramework.paper.paper import Paper
from qtPrintFramework.paper.custom import CustomPaper
from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.orientation import Orientation



class Settingsable(object):
  '''
  Mixin behaviour for PageSetup.
  Persists itself to/from Settings.
  
  A NonNative printer (PDF 'printer') does not own a persistent page setup,
  i.e. the platform doesn't necessarily know of the printer, let alone know its page setup.
  The app persists a PageSetup for such printers.
  
  A user might have used another real or native paperless printer since this app was last used.
  This PageSetup (and its persistent value)
  should be tryImpressed on adatped printer before it's dialogs are shown.
  Otherwise, the dialogs may show persistent (persisted by the platform) page setup
  of the adapted printer, or some other page setup.
  After user accepts such a dialog, we capture its page setup to self.
  '''
  
  
  def initializeModelFromSettings(self, getDefaultsFromPrinterAdaptor=None):
    #if not printerAdaptor.isAdaptingNative():
    self.fromSettings(getDefaultsFromPrinterAdaptor=getDefaultsFromPrinterAdaptor)

    
  '''
  To/from settings.
  
  Assert that QSettings have been established on client app startup:
  QCoreApplication.setOrganizationName("Foo")
  QCoreApplication.setOrganizationDomain("foo.com")
  QCoreApplication.setApplicationName("Bar")
  
  toSettings is called in reaction to dialog accept see PrintRelatedConverser.
  '''
  
  def fromSettings(self, getDefaultsFromPrinterAdaptor=None):
    '''
    Set my values from settings (that persist across app sessions.)
    
    If settings don't exist yet (first run of app after installation), 
    AND a printerAdaptor is passed, default my values from printerAdaptor.
    
    '''
    qsettings = QSettings()
    qsettings.beginGroup( "paperlessPrinter" )  # TODO better name
    
    # Prepare default values
    if getDefaultsFromPrinterAdaptor is not None:
      defaultPaperEnum = getDefaultsFromPrinterAdaptor.paper().paperEnum
      defaultOrientation = getDefaultsFromPrinterAdaptor.orientation()
    else:
      defaultPaperEnum = 0  # Hack TODO PaperSizeModel.default()
      defaultOrientation = 0  # PageOrientationModel.default()
    defaultSize = CustomPaper.defaultSize()
    
    # Get settings
    enumValue = qsettings.value( "paperEnum", defaultPaperEnum)
    orientationValue = qsettings.value( "paperOrientation", defaultOrientation )
    integralOrientedWidthValue = qsettings.value( "paperintegralOrientedWidth", defaultSize.width())
    integralOrientedHeightValue = qsettings.value( "paperintegralOrientedHeight", defaultSize.height())
    
    # Copy settings to self
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
    ## This crashes on decode exception OSX
    ##print("PageSetup from settings:", str(self))
  
  
  def toSettings(self):
    '''
    Save my values to settings.
    '''
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
