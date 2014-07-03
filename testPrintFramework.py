'''
Qt app that exercises qtPrintFramework

???
- that dialogs are foobar in certain versions of Qt (4.8) on Linux
- that dialog modes are foobar on certain platforms
- that the warning about 'non-native printer' is present on all platforms for a PDF printer.
'''

import sys

from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from qtPrintFramework.printRelatedConverser import PrintConverser
from qtPrintFramework.printerSet import printerSet
        
    

class ButtonSet(QWidget):
  '''
  Set of buttons to a PrintConverser.
  
  Widget having vertical layout of set of buttons.
  '''
  
  def __init__(self, printConverser):
    super(ButtonSet, self).__init__()
    
    layout = QVBoxLayout()
  
    # Dispatches to native or non-native page setup dialog according to current printer
    button = QPushButton("Page Setup native if current printer is native.")
    button.clicked.connect(printConverser.conversePageSetup)
    
    # Use this framework's (non-native) dialog and apply it to QPrinter
    button2 = QPushButton("Page Setup using framework dialog for native and non-native printer.")
    button2.clicked.connect(printConverser.conversePageSetupNonNative)
    
    button3 = QPushButton("Print")
    button3.clicked.connect(printConverser.conversePrint)
    
    button4 = QPushButton("Print PDF")
    button4.clicked.connect(printConverser.conversePrintPDF)
    
    layout.addWidget(button)
    layout.addWidget(button2)
    layout.addWidget(button3)
    layout.addWidget(button4)
    
    self.setLayout(layout)
    

class MainWindow(QMainWindow):
  
  def __init__(self):
    super(MainWindow, self).__init__()
    self.setGeometry(100, 100, 500, 40)
    self.printConverser = PrintConverser(parentWidget=self)
    self.connectPrintConverserSignals()
    self.setCentralWidget(ButtonSet(printConverser=self.printConverser))
    
    print("Is physical printer?:", printerSet.isPhysicalPrinterConfigured())
    printerSet.dumpAvailablePrinters()
    
    
  def connectPrintConverserSignals(self):
    self.printConverser.userChangedPaper.connect(self.changedPaper)
    # userChangedPrinter
    
    self.printConverser.userAcceptedPrint.connect(self.acceptedPrint)
    self.printConverser.userAcceptedPageSetup.connect(self.acceptedPageSetup)
    self.printConverser.userAcceptedPrintPDF.connect(self.acceptedPrintPDF)
    
    self.printConverser.userCanceledPrintRelatedConversation.connect(self.canceled)
    
  
  '''
  Dummy postludes.
  These should do something: print, or appropriate processing, such as change visible page.
  Missing: paint to printer
  '''
  def changedPaper(self):
    print(">>>Changed paper, page setup is", self.printConverser.pageSetup)
    pass
    
  def acceptedPrint(self):
    print(">>>Accepted print to printable size inch", self.printConverser.printablePageSizeInch())
    pass
    
  def acceptedPrintPDF(self):
    print(">>>Accepted Print PDF (not implemented)", self.printConverser.pageSetup)
    pass
    
  def acceptedPageSetup(self):
    print(">>>Accepted page setup is", self.printConverser.pageSetup)
    pass
    
  def canceled(self):
    pass
    
    
def main():
  app = QApplication(sys.argv)
  
  QCoreApplication.setOrganizationName("testPrintFramework")
  QCoreApplication.setOrganizationDomain("testPrintFramework.com")
  QCoreApplication.setApplicationName("testPrintFramework")
  
  # To test translations, in shell  >export LANG=es     or >export LANG=cn
  translator = QTranslator()
  result = translator.load("/home/bootch/Downloads/SubprojectsPensool/qtPrintFramework/resources/translations/qtPrintFramework_es.qm")
  if not result:
      print("Not load translation")
      # Not a failure nor exception: program continues in default (usually English)
  if not app.installTranslator(translator):
      print("Not install translator.")
  
  mainWindow = MainWindow()
  mainWindow.show()
  sys.exit(app.exec_())



if __name__=="__main__":
    main()