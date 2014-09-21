
from PyQt5.QtCore import QSettings, QSize

from qtPrintFramework.paper.paper import Paper
from qtPrintFramework.paper.custom import CustomPaper
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
  
  
  def initializeModelFromSettings(self, getDefaultsFromPrinterAdaptor):
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
    ## This crashes on decode exception OSX
    ##print("PageSetup from settings:", str(self))
  
  
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

