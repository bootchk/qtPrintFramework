

from qtPrintFramework.userInterface.dialog.pageSetup import PageSetupDialog
from qtPrintFramework.model.paperSizeFromPrinter import PrinterPaperSizeModel
from qtPrintFramework.translations import Translations


class RealPrinterPageSetupDialog(PageSetupDialog):
  
  '''
  PageSetupDialog for a real printer
  Title and paperSize model depend on adapted printer in printerAdaptor at time dialog is created.
  
  If user chooses another printer on printerAdaptor, you should create a new dialog,
  or keep a dialog for each adaptedPrinter
  '''
  
  def __init__(self, parentWidget=None, printerAdaptor=None):
    
    # ask printerAdaptor for paperSize model of adapted printer
    paperSizeModel = PrinterPaperSizeModel(printerAdaptor=printerAdaptor)
    # !!! Current implementation omits custom pages sizes.
    
    translations = Translations()
    title = translations.PageSetup + printerAdaptor.adaptedPrinterName
    
    super(RealPrinterPageSetupDialog, self).__init__(parentWidget=parentWidget, title=title, paperSizeModel=paperSizeModel)
    