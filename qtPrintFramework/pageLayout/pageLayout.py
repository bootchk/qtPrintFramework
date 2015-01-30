
from PyQt5.QtCore import pyqtProperty, QObject
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot

'''
!! This should be independent of QtPrintSupport.
If necessary, use QPageLayout (since Qt5.3) instead of QPrinter for enums.
#from PyQt5.QtGui import QPageSize # QPageLayout, 
'''

from qtPrintFramework.pageLayout.components.paper.standard import StandardPaper
from qtPrintFramework.pageLayout.components.orientation import Orientation
#from qtPrintFramework.paper.custom import CustomPaper

# Mixins
from qtPrintFramework.pageLayout.able.settingsable import Settingsable
#from qtEmbeddedQmlFramework.qmlDelegate import QmlDelegate


'''
Derived from PageSetup.py during implementation of QML PageSetup dialog.
PageSetup.py was flawed, it knew the view (editor.)  A model should not know any views on itself.
'''


# WAS a object, no signals or tr(), and is copy()'d
class PageLayout(QObject, Settingsable):  
  '''
  Persistent user's choice of page layout attributes.
  Basically a QPageLayout (new to Qt5.3) that also persists in settings.
  
  A PageLayout is data, a PageSetup is a dialog or user interaction to edit a PageLayout.
  
  This defines the set of attributes:
  - page size
  - page orientation
  - (currently, we omit margins)
  
  The editor (a dialog) defines the labels and models for attribute controls.
  
  For a CustomPaper, we DO persist user's choice of size for the Custom paper.
  
  Responsibilities:
  - editable via a PageSetupDialog
    (user can also edit a page layout using a native dialog, but that comes here via PrinterAdaptor 
  - save/restore self to settings, so self persists with app, not with a printer
  - apply/get self to/from PrinterAdaptor (via native dialogs.)
  
  Almost a responsibility:
  - edit: a PageSetupDialog edits this, and knows this intimately by iterating over editable PageAttributes.
    But other dialogs (native) contribute to self state.
    See PrintRelatedConverser.
    Editor is also known as control/view.
  
  For some apps, a PageLayout (as a user choice) is an attribute of a document.
  For other apps, a PageLayout is only an attribute of a user (a setting.)
  Here, we always get it as a setting.
  If your app treats a PageLayout as a document attribute,
  you must call toPrinterAdaptor() (but it may not take.)
  
  !!! A PageLayout can be impressed on a PrinterAdaptor, but a PrinterAdaptor does not own one.
  A PrintConverser owns a PageLayout.
  An adapted printer (that a PrinterAdaptor adapts) might own another object (opaque to us) that is its notion of page layout.
  
  !!! Paper/Page are not interchangeable but refer to a similar concept.
  Paper connotes real thing, and Page an ideal concept.
  They are often both confusingly used for the ideal concept (regardless of whether real thing is involved.)
  '''
  
  '''
  Since superclass mixin QmlDelegate defines signals, this class cannot.
  But its attributes have properties that have signals.
  IOW, this class has-a attributes that are QObjects.
  
  orientationChanged = pyqtSignal()
  paperChanged = pyqtSignal()
  '''
  
  openView = Signal() # to QML view
  accepted = Signal() # to model
  rejected = Signal() # to model
  
  
  def __init__(self, printerAdaptor=None):
    super().__init__()  # Must init QObject 
    
    '''
    A PageLayout is basically a structured model (a set of properties.)
    The properties are classes themselves (not intrinsic objects such as ints.)
    Initialized to defaults for the properties.
    PageSetup.py initialized from an editor's defaults.
    '''
    self.paper = StandardPaper(initialValue = None)
    self.orientation = Orientation(initialValue = None )
    
    " Possibly change defaults from settings AND/OR printerAdaptor."
    self.initializeModelFromSettings(getDefaultsFromPrinterAdaptor=printerAdaptor)
    # Not assert that printerAdaptor equals self yet.
    
    '''
    Is is NOT an assertion that model equals editor.
    We only ensure that just before showing dialog.
    
    It is NOT an assertion that self.isEqualPrinterAdaptor(printerAdaptor)
    in the case that printerAdaptor is adapting a native printer.
    That is, we don't force a native printer's pageLayout onto self (on user's preferred pageLayout for document),
    until user actually chooses to print on said native printer.
    '''
  
  
  """
  def __repr__(self):
    '''
    Not strict: result will not recreate object.
    TODO should be __str__
    
    paperName orientationName orientedDimensions
    e.g. 'A4 Landscape 297x219mm'
    e.g. 'Custom Portrait 640x480mm'
    '''
    ## return ','.join((str(self.paper), str(self.orientation)))  @pyqtProperty(int, notify=paperChanged)
  def paper(self):
    return self._paper
  
  @paper.setter
  def paper(self, newValue):
    self._paper = newValue
    self.paperChanged.emit()
    return self.paper.orientedDescription(self.orientation)
    ##return " ".joint((self.paper.name, self._orientationName(self.orientation)), self.paper)
  """
  
  def __eq__(self, other):
    return self.paper == other.paper and self.orientation == other.orientation

  def __str__(self):
    return 'Paper:' + str(self.paper) + ' Orientation:' +  str(self.orientation)
  
  
  def paperIsCustom(self):
    return self.paper.isCustom
  
  '''
  CRUFT from  PageSetup.py
  
  Model values to/from editors
  Exported to printRelatedConverser.
  Editor diverges from model while dialog is active.
  When dialog is accepted (and if canceled, before showing editor again) editor and model are made equal again.
  
  Since there are a mix of dialogs (native and non-native),
  and since there are other situations where a PageSetup is not supported by an editor
  (e.g. printer has been removed since settings created)
  caller should call isCompatibleWithEditor()
  '''
  
  def isCompatibleWithEditor(self, editor):
    '''
    Not used for QML
    '''
    return True
  
  
  def toEditor(self, editor):
    pass  # Not used for QML
  
  def fromEditor(self, editor):
    pass  # Not used for QML
    
    
  def dump(self):
    '''
    For debugging only, may crash decoding on other languages.
    '''
    print(self.paper, self.orientation)


  '''
  Attributes are property (so QML can access)
  Not just an int enum, but a full-fledged object.
  '''
  @pyqtProperty(Orientation)
  def orientation(self):
    return self._orientation
  
  @orientation.setter
  def orientation(self, newValue):
    self._orientation = newValue
  
  @pyqtProperty(StandardPaper)
  def paper(self):
    return self._paper
  
  @paper.setter
  def paper(self, newValue):
    self._paper = newValue
    
    
  def emitOpenView(self):
    '''
    Activate view of self (self as a model.)
    Called from business side.
    Connected in QML to Dialog.open()
    '''
    print("activate called, emitting openView")
    self.openView.emit()
  
  '''
  Alias
  From business side, open means "window modal."
  That semantic must be defined in the QML.
  '''
  open = emitOpenView
  
  
  @Slot()
  def accept(self):
    '''
    Called from QML side.
    Connected in business side to a handler of dialog results (in shared model.)
    '''
    self.accepted.emit()
  
  @Slot()
  def reject(self):
    '''
    Opposite cohort of accept.
    '''
    self.rejected.emit()
  