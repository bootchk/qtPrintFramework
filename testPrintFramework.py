'''
Qt app that exercises qtPrintFramework


This is a test harness for QPageSetup.

Various things tested:
- that dialogs are foobar in certain versions of Qt (4.8)
- that dialog modes are foobar on certain platforms
- that the warning about 'non-native printer' is present on all platforms for a PDF printer.
'''

import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

from qtPrintFramework.printerAdaptor import PrinterAdaptor

mainWindow = None
        
    

class ButtonSet(QWidget):
  '''
  Set of buttons to a PrintConverser.
  
  Widget having vertical layout of set of buttons.
  '''
  
  def __init__(self, printerAdaptor):
    super(ButtonSet, self).__init__()
    
    layout = QVBoxLayout()
  
    button = QPushButton("Setup page")
    button.clicked.connect(printerAdaptor.doPageSetup)
    
    """
    button2 = QPushButton("Setup page PDF non-native")
    button2.clicked.connect(printerAdaptor.doPageSetupDefaultPDFPrinter)
    """
    button3 = QPushButton("Print")
    button3.clicked.connect(printerAdaptor.doPrint)
    
    """
    button4 = QPushButton("Print PDF")
    button4.clicked.connect(printerAdaptor.doPrintPDF)
    
    
    button5 = QPushButton("Private Page Setup")
    button5.clicked.connect(printerAdaptor.doPrivatePageSetup)
    """
    
    layout.addWidget(button)
    #layout.addWidget(button2)
    layout.addWidget(button3)
    #layout.addWidget(button4)
    #layout.addWidget(button5)
    
    self.setLayout(layout)
    
    
    
def main():
  app = QApplication(sys.argv)
  
  global mainWindow
  
  mainWindow = QMainWindow()
  mainWindow.setGeometry(100, 100, 500, 40)
  
  # printConverser = PrintConverser(parentWidget=mainWindow)
  printerAdaptor = PrinterAdaptor(parentWidget=mainWindow)
  
  mainWindow.setCentralWidget(ButtonSet(printerAdaptor=printerAdaptor))
  mainWindow.show()

  
  
  sys.exit(app.exec_())



if __name__=="__main__":
    main()