
from PyQt5.QtGui import QPagedPaintDevice  

# !! This should be independent of QtPrintSupport.
# Instead, use QPageLayout (since Qt5.3) instead of QPrinter for enums 

# Mixins
from qtPrintFramework.pageSetup.settingsable import Settingsable


from qtPrintFramework.paper.standard import StandardPaper
from qtPrintFramework.paper.custom import CustomPaper

from qtPrintFramework.orientation import Orientation
from qtPrintFramework.alertLog import alertLog



class PageSetup(Settingsable, object):  # Not a QObject, no signals or tr(), and is copy()'d
  '''
  Persistent user's choice of page setup attributes.
  Basically a QPageLayout (new to Qt5.3) that also persists in settings.
  
  This defines the set of attributes:
  - page size
  - page orientation
  - (currently, we omit margins)
  
  The editor (a dialog) defines the labels and models for attribute controls.
  
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
  
  def __init__(self, masterEditor, printerAdaptor=None):
    
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
    We only ensure that just before showing dialog.
    
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
    Are self's values supported by editor's control's models?
    
    !!! Not checking orientation, only paper kind.
    Compile time assertion that all editors support all known values of orientation.
    '''
    result = editor.sizeControl.isValueInModel(self.paper.paperEnum)
    return result
  
  
    
  def toEditor(self, editor):
    '''
    Set value of editor to self's values.
    
    When editor does not support self values, set to a default.
    Typically, editor does not support Custom paper.
    '''
    # When value not in model, this sets it to a default.
    editor.sizeControl.setValue(self.paper.paperEnum)
    
    editor.orientationControl.setValue(self.orientation.value)
    assert self._isModelWeaklyEqualEditor(editor)
    
  """
  def toEditorExcludeCustom(self, editor):
    '''
    To editor, except if self is Custom,
    select another default value in editor.
    (Before displaying editor, we will warn the user that the editor
    does permit editing a Custom PageSetup.)
    '''
    if self.paper.paperEnum == QPrinter.Custom:
      # Not allow Custom into dialog
      editor.sizeControl.setValue(0) # Typically A4 ?
    else:
      editor.sizeControl.setValue(self.paper.paperEnum)
    editor.orientationControl.setValue(self.orientation.value)
    assert self._isModelWeaklyEqualEditor(editor)
  """
  
  def fromEditor(self, editor):
    ''' 
    NonNative PageSetup Dialog was accepted.  Capture values from editor to model.
    
    Dialog DOES allow choice of Custom, but not specifying size: will default.
    
    Since Dialog defaults size of Custom, Dialog cannot be used to just change
    the orientation of an existing Custom paper???
    '''
    # Orientation choice is meaningful even if paper is Custom with default size?
    self.orientation = Orientation(editor.orientationControl.value)
    
    # Create new instance of Paper from enum.  Old instance garbage collected.
    self.paper = self._paperFromEnum(editor.sizeControl.value)
    
    assert self._isModelWeaklyEqualEditor(editor)
    
  
  '''
  Assertion support
  '''
  def _isModelWeaklyEqualEditor(self, editor):
    '''
    Is editor showing self's values.
    
    Allow one disparity: self has value that editor does not support (typically Custom)
    and editor has default value of 0.  See toEditor.
    '''
    result = ( self.paper.paperEnum == editor.sizeControl.value \
               or editor.sizeControl.value == 0) \
          and self.orientation.value == editor.orientationControl.value
    if not result:
      alertLog("pageSetup weakly differs")
      #print(self.paper, self.orientation, editor.sizeControl.value, editor.orientationControl.value)
    return result
  
  
    
  def _paperFromEnum(self, paperEnum):
    '''
    Instance of a subclass of Paper for paperEnum.
    
    If Custom, default size.
    '''
    assert isinstance(paperEnum, int), str(type(paperEnum))
    if paperEnum == QPagedPaintDevice.Custom:
      # TODO warning dialog here
      alertLog("PageSetup sets Custom paper to default size.  You may change size when you Print. ")
      result = CustomPaper(integralOrientedSizeMM=CustomPaper.defaultSize(),
                           orientation=Orientation()) # default to Portrait
    else:
      result = StandardPaper(paperEnum)
    return result

    
    
    
  def dump(self):
    '''
    For debugging only, may crash decoding on other languages.
    '''
    print(self.paper, self.orientation)

  