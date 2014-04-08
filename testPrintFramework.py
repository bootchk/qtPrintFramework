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
from qtPrintFramework.printerAdaptor import PrinterAdaptor
        
    

class ButtonSet(QWidget):
  '''
  Set of buttons to a PrintConverser.
  
  Widget having vertical layout of set of buttons.
  '''
  
  def __init__(self, printerAdaptor):
    super(ButtonSet, self).__init__()
    
    layout = QVBoxLayout()
  
    button = QPushButton("Setup page")
    button.clicked.connect(printerAdaptor.conversePageSetup)
    
    button2 = QPushButton("Print PDF")
    button2.clicked.connect(printerAdaptor.conversePrintPDF)
    
    button3 = QPushButton("Print")
    button3.clicked.connect(printerAdaptor.conversePrint)
    
    layout.addWidget(button)
    layout.addWidget(button2)
    layout.addWidget(button3)
    
    self.setLayout(layout)
    

class MainWindow(QMainWindow):
  
  def __init__(self):
    super(MainWindow, self).__init__()
    self.setGeometry(100, 100, 500, 40)
    self.printerAdaptor = PrinterAdaptor(parentWidget=self)
    self.connectPrinterAdaptorSignals(self.printerAdaptor)
    self.setCentralWidget(ButtonSet(printerAdaptor=self.printerAdaptor))
    
    
  def connectPrinterAdaptorSignals(self, printerAdaptor):
    printerAdaptor.printConverser.userChangedPaper.connect(self.changedPaper)
    # userChangedPrinter
    
    printerAdaptor.printConverser.userAcceptedPrint.connect(self.acceptedPrint)
    printerAdaptor.printConverser.userAcceptedPageSetup.connect(self.acceptedPageSetup)
    printerAdaptor.printConverser.userAcceptedPrintPDF.connect(self.acceptedPrintPDF)
    
    printerAdaptor.printConverser.userCanceledPrintRelatedConversation.connect(self.canceled)
    
  
  '''
  Dummy postludes.
  These should do something: print, or appropriate processing, such as change visible page.
  '''
  def changedPaper(self):
    print(">>>>>>>user changed paper")
    
  def acceptedPrint(self):
    print(">>>>>>>user accepted print")
    
  def acceptedPrintPDF(self):
    print(">>>>>>>user accepted print pdf")
    
  def acceptedPageSetup(self):
    print(">>>>>>>user accepted page setup")
    
  def canceled(self):
    print(">>>>>>>user canceled")
    
    
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