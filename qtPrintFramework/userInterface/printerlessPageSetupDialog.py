
import sys

from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

from qtPrintFramework.userInterface.pageSetupForm import PageSetupForm
from qtPrintFramework.pageAttribute import PageAttribute
from qtPrintFramework.model.paperSize import AdaptedPaperSizeModel 
from qtPrintFramework.model.pageOrientation import AdaptedPageOrientationModel 


class PrinterlessPageSetupDialog(QDialog):
  
  '''
  An editor (view/controller) for PageSetup model.
  
  Needed because QPageSetupDialog 'cannot be used with non-native printers.' 
  i.e. a PDFWriter when Qt is in charge, on Linux and Win.
  
  Some platforms have native print drivers that are printerless i.e. to-file.
  OSX : PDF
  Win : XPS
  
  Should look similar to QPageSetupDialog.
  
  For now, this omits margins as a feature of PageSetup.
  '''
  
  def __init__(self, parentWidget=None):

    super(PrinterlessPageSetupDialog, self).__init__(parent=parentWidget)
    
    # Models for controls
    self.pageOrientationModel = AdaptedPageOrientationModel()
    self.paperSizeModel = AdaptedPaperSizeModel() 
    
    # Properties, i.e. label/control rows
    self.sizeControl = PageAttribute(label=self.tr("Size"),  model=self.paperSizeModel)
    self.orientationControl = PageAttribute(label=self.tr("Orientation"), model=self.pageOrientationModel)
    
    # Layout components
    dialogLayout = QVBoxLayout()
    
    title = self.tr('Page Setup') # OR 'Page Setup PDF' if you also use the native dialog
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
  
  