

from qtPrintFramework.userInterface.widget.dialog.pageSetup import PageSetupDialog

from qtPrintFramework.pageLayout.model.paperSize import AdaptedPaperSizeModel
from qtPrintFramework.translations import Translations



class PrinterlessPageSetupDialog(PageSetupDialog):
  
  '''
  PageSetupDialog for printerless printing, i.e. 'To File', sometimes called PDF.
  Title and paperSize model is static.
  '''
  
  def __init__(self, parentWidget=None):
    
    paperSizeModel = AdaptedPaperSizeModel()
    translations = Translations()
    title = translations.PageSetupPDF
    super(PrinterlessPageSetupDialog, self).__init__(parentWidget=parentWidget, title=title, paperSizeModel=paperSizeModel)
    