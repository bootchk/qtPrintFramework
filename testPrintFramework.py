'''
Qt app that exercises qtPrintFramework

???
- that dialogs are foobar in certain versions of Qt (4.8) on Linux
- that dialog modes are foobar on certain platforms
- that the warning about 'non-native printer' is present on all platforms for a PDF printer.
'''

import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from qtPrintFramework.printRelatedConverser import PrintConverser
        
    

class ButtonSet(QWidget):
  '''
  Set of buttons to a PrintConverser.
  
  Widget having vertical layout of set of buttons.
  '''
  
  def __init__(self, printConverser):
    super(ButtonSet, self).__init__()
    
    layout = QVBoxLayout()
  
    button = QPushButton("Setup page")
    button.clicked.connect(printConverser.conversePageSetup)
    
    button2 = QPushButton("Print PDF")
    button2.clicked.connect(printConverser.conversePrintPDF)
    
    button3 = QPushButton("Print")
    button3.clicked.connect(printConverser.conversePrint)
    
    layout.addWidget(button)
    layout.addWidget(button2)
    layout.addWidget(button3)
    
    self.setLayout(layout)
    

class MainWindow(QMainWindow):
  
  def __init__(self):
    super(MainWindow, self).__init__()
    self.setGeometry(100, 100, 500, 40)
    self.printConverser = PrintConverser(parentWidget=self)
    self.connectPrintConverserSignals()
    self.setCentralWidget(ButtonSet(printConverser=self.printConverser))
    
    
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
    print(">>>Page setup is", self.printConverser.pageSetup)
    pass
    
  def acceptedPrint(self):
    print(">>>Printing to size", self.printConverser.printablePageSize)
    pass
    
  def acceptedPrintPDF(self):
    pass
    
  def acceptedPageSetup(self):
    print(">>>Page setup is", self.printConverser.pageSetup)
    pass
    
  def canceled(self):
    pass
    
    
def main():
  app = QApplication(sys.argv)
  
  QCoreApplication.setOrganizationName("testPrintFramework")
  QCoreApplication.setOrganizationDomain("testPrintFramework.com")
  QCoreApplication.setApplicationName("testPrintFramework")
  
  mainWindow = MainWindow()
  mainWindow.show()
  sys.exit(app.exec_())



if __name__=="__main__":
    main()