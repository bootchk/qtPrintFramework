
from PyQt5.QtPrintSupport import QPrinterInfo



class PrinterSet(object):
  '''
  Set of printers on user's system.
  
  Wrapper on QPrinterInfo
  '''
  
  def isPhysicalPrinterConfigured(self):
    '''
    AKA is printer installed.
    
    This does NOT return True if the OS would only allow printing to a file.
    The print dialog should still open in that case on most platforms.
    
    But a bug in Qt refuses to open the native print dialog on OSX in that case.
    So typical use of this method:
    if it returns false and platform is OSX, disable print action that would open a Print dialog
    (or to give a message 'Please configure a physical printer.')
    so the user doesn't see the Qt bug.
    '''
    # not available until Qt5.3
    # printerNames = QPrinterInfo.availablePrinterNames()
    
    return len(self.availablePrinters()) > 0
    
    
  def availablePrinters(self):
    return QPrinterInfo.availablePrinters()
  
    
  def dumpAvailablePrinters(self):
    printerList = self.availablePrinters()
    print("Available printers:")
    for printerInfo in printerList:
      print(printerInfo.printerName())


printerSet = PrinterSet()
