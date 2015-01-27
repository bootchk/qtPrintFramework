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

from qtPrintFramework.converser.printered import PrinteredConverser
from qtPrintFramework.converser.unprintered import UnprinteredConverser
from qtPrintFramework.printer.printerSet import printerSet

import qtPrintFramework.config as config
    

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
    ## Choose one to debug
    self.printConverser = PrinteredConverser(parentWidget=self)
    ## self.printConverser = UnprinteredConverser(parentWidget=self)
    self.connectPrintConverserSignals()
    self.setCentralWidget(ButtonSet(printConverser=self.printConverser))
    
    print("Is physical printer?:", printerSet.isPhysicalPrinterConfigured())
    printerSet.dumpAvailablePrinters()
    
    
  def connectPrintConverserSignals(self):
    self.printConverser.userChangedLayout[int].connect(self.changedLayout)
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
  def changedLayout(self, value):
    print(">>>Changed layout(paper or orientation), page layout is", self.printConverser.pageLayout)
    pass
    
  def acceptedPrint(self):
    print(">>>Accepted print to printable size inch", self.printConverser.printablePageSizeInch())
    pass
    
  def acceptedPrintPDF(self):
    print(">>>Accepted Print PDF (not implemented)", self.printConverser.pageLayout)
    pass
    
  def acceptedPageSetup(self):
    print(">>>Accepted page setup is", self.printConverser.pageLayout)
    pass
    
  def canceled(self):
    pass
    
    
def main():
  sys.setrecursionlimit(60)  # to find infinite signal loops?
  
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
  
  if config.useQML:
    from qtEmbeddedQmlFramework.resourceManager import resourceMgr
    resourceMgr.setResourceRoot(__file__, 'qtPrintFramework')
    
  mainWindow = MainWindow()
  mainWindow.show()
  sys.exit(app.exec_())



if __name__=="__main__":
    main()