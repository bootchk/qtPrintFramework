
import sys

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

from qtPrintFramework.userInterface.pageSetupForm import PageSetupForm
from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.pageOrientation import AdaptedPageOrientationModel
from qtPrintFramework.translations import Translations


class PageSetupDialog(QDialog):
  
  '''
  An editor (view/controller) for PageSetup model.
  
  Needed because QPageSetupDialog 'cannot be used with non-native printers.' 
  i.e. a PDFWriter when Qt is in charge, on Linux and Win.
  
  Some platforms have native print drivers that are printerless i.e. to-file.
  OSX : PDF
  Win : XPS
  
  Should look similar to QPageSetupDialog.
  
  For now, this omits margins as a feature of PageSetup.
  
  Inherited by:
  - PrinterlessPageSetup
  - RealPrinterPageSetup
  '''
  
  def __init__(self, parentWidget=None, title=None, paperSizeModel=None, printerAdaptor=None):

    super(PageSetupDialog, self).__init__(parent=parentWidget)
    
    # Models for controls
    self.pageOrientationModel = AdaptedPageOrientationModel()
    self.paperSizeModel = paperSizeModel
    
    # Properties, i.e. label/control rows
    translations = Translations()
    self.sizeControl = PageAttribute(label=translations.Size,  model=self.paperSizeModel)
    self.orientationControl = PageAttribute(label=translations.Orientation, model=self.pageOrientationModel)
    
    # Layout components
    dialogLayout = QVBoxLayout()
    
    # Use passed title
    if sys.platform.startswith('darwin'):
      # GUI sheet has no title bar
      dialogLayout.addWidget(QLabel(title))
    else:
      self.setWindowTitle(title)
      
    dialogLayout.addLayout(self._createDialogBody())
    dialogLayout.addWidget(self.buttonBox())
    self.setLayout(dialogLayout)
    
    #self.setDisabled(not self.isEditable())
    self.setSizeGripEnabled(True)
    
    
    
  def _createDialogBody(self):
    '''
    Create body of dialog, on self's primitive controls.
    '''
    return PageSetupForm(controls=(self.sizeControl, self.orientationControl))
  
  
  def buttonBox(self):
    " buttonBox, with connected signals"
    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok
                                 | QDialogButtonBox.Cancel)
    # button signals connected to QDialog signal handlers, which in turn emit
    buttonBox.accepted.connect(self.accept)
    buttonBox.rejected.connect(self.reject)
    return buttonBox
  
  